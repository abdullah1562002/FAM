import pandas as pd

class FAM:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.Flight_Schedule = pd.DataFrame()
        self.Stations = []
        self.Nodes = []
        self.ground_links = []
        self.Variables = []
        self.Number_fleets = 2
        self.Number_of_ground_links = 0
        self.Number_Stations = 0
        self.Number_Flights = 0
        self.Number_of_Nodes = 0
        self.Number_of_Variables = 0
        self.Number_of_Coverage_Constraints = 0
        self.Number_of_Resource_Constraints = 0
        self.Number_of_Balance_Constraints = 0

    def read_flight_schedule(self):
        self.Flight_Schedule = pd.DataFrame(pd.read_excel(self.excel_file, index_col=None, engine="openpyxl"))
        self.Number_Flights = len(self.Flight_Schedule)

    def identify_stations(self):
        for flight in self.Flight_Schedule.index:
            if self.Flight_Schedule["from"][flight] not in self.Stations:
                self.Stations.append(self.Flight_Schedule["from"][flight])
        
        self.Number_Stations = len(self.Stations)
                       

    def create_empty_node(self, node_number, station_name):
        new_node = {
            "Node" : node_number,
            "Station" : station_name,
            "Inbound" : [],
            "Outbound" : []
        } 
        return new_node

    def create_nodes(self):
        for station in self.Stations:
            Number_of_Nodes = len(self.Nodes)
            new_node = self.create_empty_node(Number_of_Nodes + 1, station)

            station_schedule = self.Flight_Schedule[(self.Flight_Schedule["from"] == station) | (self.Flight_Schedule["to"] == station)]
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
                if station == station_schedule["to"][flight]:
                    if flight == 0:
                        new_node["Inbound"].append(f"RON_{station}")
                        new_node["Inbound"].append(station_schedule["flight number"][flight])
                    elif flight == station_flights - 1:
                        new_node["Inbound"].append(station_schedule["flight number"][flight])
                        new_node["Outbound"].append(f"RON_{station}")
                    else:
                        new_node["Inbound"].append(station_schedule["flight number"][flight])
                elif station == station_schedule["from"][flight]:
                    if flight == 0:
                        new_node["Inbound"].append(f"RON_{station}")
                        if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1]:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])
                            self.Nodes.append(new_node)
                            Number_of_Nodes = len(self.Nodes)
                            new_node = self.create_empty_node(Number_of_Nodes + 1, station)
                        else:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])
                    elif flight == station_flights - 1:
                        if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1]:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])
                            self.Nodes.append(new_node)
                            Number_of_Nodes = len(self.Nodes)
                            new_node = self.create_empty_node(Number_of_Nodes + 1, station)
                        else:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])
                        new_node["Outbound"].append(f"RON_{station}")
                    else:
                        if flight != (station_flights - 1) and station == station_schedule["to"][flight + 1]:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])
                            self.Nodes.append(new_node)
                            Number_of_Nodes = len(self.Nodes)
                            new_node = self.create_empty_node(Number_of_Nodes + 1, station)
                        else:
                            new_node["Outbound"].append(station_schedule["flight number"][flight])

            self.Nodes.append(new_node)
            self.Number_of_Nodes = len(self.Nodes)
            
            

    def create_ground_links(self):
        for Station in self.Stations:
            for node in range(self.Number_of_Nodes - 1):
                if self.Nodes[node]["Station"] == Station and self.Nodes[node + 1]["Station"] == Station:
                    ground_link = f"y({node + 1}-{node + 2})"
                    self.ground_links.append(ground_link)
                    self.Nodes[node]["Outbound"].append(ground_link)
                    self.Nodes[node + 1]["Inbound"].insert(0, ground_link)
        
        # check ground links = Number_of_Nodes - RONs
        if len(self.ground_links) == self.Number_of_Nodes - self.Number_Stations: 
            self.Number_of_ground_links = len(self.ground_links)
        
        self.Number_of_Variables = (self.Number_Flights + self.Number_Stations + self.Number_of_ground_links)*self.Number_fleets 
        self.Number_of_Coverage_Constraints = self.Number_Flights
        self.Number_of_Resource_Constraints = self.Number_fleets
        self.Number_of_Balance_Constraints = self.Number_of_Nodes*self.Number_fleets


    def  constraints_matrices(self):
        
        # Coverage Vaiables
        for flight in self.Flight_Schedule["flight number"]:
            for fleet in range(self.Number_fleets):
                self.Variables.append(f"X{flight}_{fleet+1}")

        # Resources Variables
        for fleet in range(self.Number_fleets):
            for station in self.Stations:
                self.Variables.append(f"RON_{station}_{fleet+1}")

        # Balance (Interconnection) Variables
        for g_link in self.ground_links:
            for fleet in range(self.Number_fleets):
                self.Variables.append(f"{g_link}_{fleet+1}")


        # Coverage Matrix
        coverage_matrix = pd.DataFrame(columns=self.Variables)
        new_row = {}
                
        for flight in self.Flight_Schedule["flight number"]:
            for fleet in range(self.Number_fleets):
                new_row[f"X{flight}_{fleet+1}"] = 1
            
            
            coverage_matrix = coverage_matrix._append(new_row, ignore_index=True)
            new_row.clear()

        # Resource Matrix
        resource_matrix = pd.DataFrame(columns=self.Variables)
        new_row = {}

        for fleet in range(self.Number_fleets):
            for station in self.Stations:
                new_row[f"RON_{station}_{fleet+1}"] = 1

            
            resource_matrix = resource_matrix._append(new_row, ignore_index=True)
            new_row.clear()

        
        # Balance (Interconnection) Matrix
        Balance_matrix = pd.DataFrame(columns=self.Variables)
        new_row = {}

        for node in range(self.Number_of_Nodes):
            for fleet in range(self.Number_fleets):
                
                #Inbounds
                for In in self.Nodes[node]["Inbound"]: 
                    if type(In) is str:
                        new_row[f"{In}_{fleet+1}"] = 1
                    else:
                        new_row[f"X{In}_{fleet+1}"] = 1
                #Outbounds
                for Out in self.Nodes[node]["Outbound"]: 
                    if type(Out) is str:
                        new_row[f"{Out}_{fleet+1}"] = -1
                    else:
                        new_row[f"X{Out}_{fleet+1}"] = -1

            
                Balance_matrix = Balance_matrix._append(new_row, ignore_index=True)
                new_row.clear()
        


        # Constraint_Matrix
        constraints_matrix = pd.concat([coverage_matrix, resource_matrix, Balance_matrix], ignore_index = True).fillna(0)
        print(constraints_matrix)
        constraints_matrix.to_excel("constraints_matrix.xlsx", engine="openpyxl")

        


        



    def return_analysis(self):
        
        self.read_flight_schedule()
        self.identify_stations()
        self.create_nodes()
        self.create_ground_links()
        self.constraints_matrices()


        return self.Nodes ,self.Number_of_Variables, self.Number_Flights, self.Number_Stations, self.Number_of_ground_links

    
        
