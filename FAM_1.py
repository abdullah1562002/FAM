# FFFFFFFFFFFFFFFFFFFFFF      AAA               MMMMMMMM               MMMMMMMM
# F::::::::::::::::::::F     A:::A              M:::::::M             M:::::::M
# F::::::::::::::::::::F    A:::::A             M::::::::M           M::::::::M
# FF::::::FFFFFFFFF::::F   A:::::::A            M:::::::::M         M:::::::::M
#   F:::::F       FFFFFF  A:::::::::A           M::::::::::M       M::::::::::M
#   F:::::F              A:::::A:::::A          M:::::::::::M     M:::::::::::M
#   F::::::FFFFFFFFFF   A:::::A A:::::A         M:::::::M::::M   M::::M:::::::M
#   F:::::::::::::::F  A:::::A   A:::::A        M::::::M M::::M M::::M M::::::M
#   F:::::::::::::::F A:::::A     A:::::A       M::::::M  M::::M::::M  M::::::M
#   F::::::FFFFFFFFFFA:::::AAAAAAAAA:::::A      M::::::M   M:::::::M   M::::::M
#   F:::::F         A:::::::::::::::::::::A     M::::::M    M:::::M    M::::::M
#   F:::::F        A:::::AAAAAAAAAAAAA:::::A    M::::::M     MMMMM     M::::::M
# FF:::::::FF     A:::::A             A:::::A   M::::::M               M::::::M
# F::::::::FF    A:::::A               A:::::A  M::::::M               M::::::M
# F::::::::FF   A:::::A                 A:::::A M::::::M               M::::::M
# FFFFFFFFFFF  AAAAAAA                   AAAAAAAMMMMMMMM               MMMMMMMM
                                                                             
import pandas as pd




# Read Flight Schedule 
Flight_Schedule = pd.DataFrame(pd.read_excel("Time Schedule.xlsx", index_col=None, engine="openpyxl"))



# Identify Stations 
Stations = []

for flight in Flight_Schedule.index:
    if Flight_Schedule["from"][flight] not in Stations:
        Stations.append(Flight_Schedule["from"][flight])




# Calculate Number of Stations and Number of Flights
Number_Stations = len(Stations)
Number_Flights = len(Flight_Schedule)




# Node Creation
Nodes = []
ground_links = []

def create_empty_node(node_number, station_name):
    new_node = {
        "Node" : node_number,
        "Station" : station_name,
        "Inbound" : [],
        "Outbound" : []

    } 
    return new_node

for station in Stations:
    Number_of_Nodes = len(Nodes)
    new_node = create_empty_node(Number_of_Nodes + 1, station)
    
    station_schedule = Flight_Schedule[(Flight_Schedule["from"] == station) | (Flight_Schedule["to"] == station)]
    station_schedule = station_schedule.reset_index(drop=True)
    station_schedule["Station Time"] = ""
    station_flights = len(station_schedule)


    for flight in station_schedule.index:
        if station == station_schedule["to"][flight]:
           station_schedule.loc[flight, "Station Time"] = station_schedule.loc[flight, "Arrival"]

        elif station == station_schedule["from"][flight]:
           station_schedule.loc[flight, "Station Time"] = station_schedule.loc[flight, "Departure"]

    station_schedule = station_schedule.sort_values(['Station Time'])
    station_schedule = station_schedule.reset_index(drop=True)


    for flight in station_schedule.index:
        
        # open Node if Arrival Found
        if station == station_schedule["to"][flight]:
           if flight == 0:
                new_node["Inbound"].append(f"RON_{station}")
                new_node["Inbound"].append(station_schedule["flight number"][flight])
           elif flight == station_flights - 1:
                new_node["Inbound"].append(station_schedule["flight number"][flight])
                new_node["Outbound"].append(f"RON_{station}")
           else:
               new_node["Inbound"].append(station_schedule["flight number"][flight])
        
        # open Node if Departure Found
        elif station == station_schedule["from"][flight]:
             if flight == 0:
                new_node["Inbound"].append(f"RON_{station}")
                if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1] :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])
                    Nodes.append(new_node)
                    Number_of_Nodes = len(Nodes)
                    new_node = create_empty_node(Number_of_Nodes + 1, station)
    
                else :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])

             elif flight == station_flights - 1:
                if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1] :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])
                    Nodes.append(new_node)
                    Number_of_Nodes = len(Nodes)
                    new_node = create_empty_node(Number_of_Nodes + 1, station)
    
                else :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])
                
                new_node["Outbound"].append(f"RON_{station}")
             
             else:
                if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1] :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])
                    Nodes.append(new_node)
                    Number_of_Nodes = len(Nodes)
                    new_node = create_empty_node(Number_of_Nodes + 1, station)
    
                else :
                    new_node["Outbound"].append(station_schedule["flight number"][flight])

    Nodes.append(new_node)
    Number_of_Nodes = len(Nodes)



for Station in Stations:
    for node in range(Number_of_Nodes - 1):
        if Nodes[node]["Station"] == Station and Nodes[node + 1]["Station"] == Station:
            ground_link = f"y({node+1}-{node+2})"
            ground_links.append(ground_link)
            Nodes[node]["Outbound"].append(ground_link)
            Nodes[node+1]["Inbound"].insert(0,ground_link)






print(ground_links)
print(Nodes)
        