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
import pyomo.environ as pe
import pyomo.opt as po
from scipy.optimize import linprog
import numpy as np
import json


class FAM:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.Flight_Schedule = pd.DataFrame()
        self.fleets = pd.DataFrame()
        self.Stations = []
        self.Nodes = []
        self.ground_links = []
        self.Variables = []
        self.Dummy_variables = []
        self.RON_variables = []
        self.ground_link_variables = [] 
        self.Number_fleets = 0
        self.Number_of_ground_links = 0
        self.Number_Stations = 0
        self.Number_Flights = 0
        self.Number_of_Nodes = 0
        self.Number_of_Variables = 0
        self.Number_of_Coverage_Constraints = 0
        self.Number_of_Resource_Constraints = 0
        self.Number_of_Balance_Constraints = 0
        self.coverage_rhs = []
        

    def read_flight_schedule(self):
        self.Flight_Schedule = pd.DataFrame(pd.read_excel(self.excel_file, sheet_name="Flights", index_col=None, engine="openpyxl"))
        self.Number_Flights = len(self.Flight_Schedule)
    
    def read_fleets(self):
        self.fleets = pd.DataFrame(pd.read_excel(self.excel_file, sheet_name="Fleets", index_col=None, engine="openpyxl"))
        self.Number_fleets = len(self.fleets)
        
        

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
                self.Dummy_variables.append(f"X{flight}_{fleet+1}")

        # Resources Variables
        for fleet in range(self.Number_fleets):
            for station in self.Stations:
                self.Variables.append(f"RON_{station}_{fleet+1}")
                self.RON_variables.append(f"RON_{station}_{fleet+1}")

        # Balance (Interconnection) Variables
        for g_link in self.ground_links:
            for fleet in range(self.Number_fleets):
                self.Variables.append(f"{g_link}_{fleet+1}")
                self.ground_link_variables.append(f"{g_link}_{fleet+1}")


        # Coverage Matrix
        self.coverage_matrix = pd.DataFrame(columns=self.Variables)
        new_row = {}
                
        for flight in self.Flight_Schedule["flight number"]:
            for fleet in range(self.Number_fleets):
                new_row[f"X{flight}_{fleet+1}"] = 1
            
            
            self.coverage_matrix = self.coverage_matrix._append(new_row, ignore_index=True)
            new_row.clear()
        
        self.coverage_matrix = self.coverage_matrix.fillna(0)
        self.coverage_matrix.to_excel("coverage_matrix.xlsx", engine="openpyxl")
        self.coverage_rhs = np.ones(self.Number_Flights)
        self.coverage_bounds = [(0,1) for i in range(len(self.Dummy_variables))]  
        
        

        # Resource Matrix
        self.resource_matrix = pd.DataFrame(columns=self.Variables)
        new_row = {}
        self.resource_bounds = []
        self.resource_rhs = []

        for fleet in range(self.Number_fleets):
            for station in self.Stations:
                new_row[f"RON_{station}_{fleet+1}"] = 1
                # max fleet in ron 
                self.resource_bounds.append((0,self.fleets["size"][fleet]))

            
            self.resource_matrix = self.resource_matrix._append(new_row, ignore_index=True)
            self.resource_rhs.append(self.fleets["size"][fleet])
            new_row.clear()
        
        self.resource_matrix = self.resource_matrix.fillna(0)
        self.resource_matrix.to_excel("resource_matrix.xlsx", engine="openpyxl")
        
        

        
        # Balance (Interconnection) Matrix
        self.Balance_matrix = pd.DataFrame(columns=self.Variables)
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

            
                self.Balance_matrix = self.Balance_matrix._append(new_row, ignore_index=True).fillna(0)
                new_row.clear()
        
        self.Balance_matrix = self.Balance_matrix.fillna(0)
        self.Balance_matrix.to_excel("Balance_matrix.xlsx", engine="openpyxl")
        self.Balance_rhs = np.zeros(len(self.Balance_matrix))
        self.Balnace_bounds = [(0,None) for i in self.ground_link_variables]
        

        self.coverage_Balance_matrix = pd.concat([self.coverage_matrix, self.Balance_matrix], ignore_index = True)
        self.coverage_Balance_rhs = np.append(self.coverage_rhs, self.Balance_rhs)
        # Constraint_Matrix
        self.constraints_matrix = pd.concat([self.coverage_matrix, self.Balance_matrix, self.resource_matrix], ignore_index = True).fillna(0)
        self.constraints_matrix.to_excel("constraints_matrix.xlsx", engine="openpyxl")

    

    def  profit_calculation(self):
        
        row = {}
        self.profit_function = pd.DataFrame(columns=self.Variables)
        for flight in self.Flight_Schedule.index:
            for fleet in range(self.Number_fleets):
                row[f"X{flight+1}_{fleet+1}"] =  self.Flight_Schedule["Fare"][flight] * min(self.fleets["capacity"][fleet], self.Flight_Schedule["Demand"][flight]) - self.fleets["cost_per_mile"][fleet] * self.Flight_Schedule["Distance"][flight]
                
        self.profit_function = self.profit_function._append(row, ignore_index=True).fillna(0)
        self.profit_function.to_excel("profit_function.xlsx", engine="openpyxl")


    
    def optimize(self):
        
        objective_function = self.profit_function.to_numpy()
        inequality_constraints = self.resource_matrix.to_numpy()
        equality_constraints = self.coverage_Balance_matrix.to_numpy()
        inequality_rhs = self.resource_rhs
        equality_rhs = self.coverage_Balance_rhs
        bounds = []
        bounds.extend(self.coverage_bounds)
        bounds.extend(self.resource_bounds)
        bounds.extend(self.Balnace_bounds)
        
        
        
        # using scipy linprog to optimize
        self.result = linprog(-objective_function,
                         A_ub = inequality_constraints,
                         b_ub = inequality_rhs,
                         A_eq = equality_constraints,
                         b_eq = equality_rhs,
                         bounds = bounds,
                         
                         
                        
        )

        # Display output
        self.output = pd.DataFrame(columns=self.Variables)
        self.output.loc[len(self.output)] = self.result.x
        self.output.to_csv("output.csv")
        self.Maximum_profit = -self.result.fun   


        print(self.Maximum_profit)
        print(self.result.x)
        print(self.output)

    def optimize_pyomo(self):

        model = pe.ConcreteModel()

       
        
        model.x = pe.Var(self.Dummy_variables, within = pe.Binary)
        model.RON = pe.Var(self.RON_variables, within = pe.NonNegativeIntegers)
        model.ground_links = pe.Var(self.ground_link_variables, within = pe.NonNegativeIntegers)

        # Coverage Constraints 
        model.coverage_constraints = pe.ConstraintList()
        for flight in self.Flight_Schedule["flight number"]:
            coverage_sum = sum([model.x[f"X{flight}_{fleet+1}"] for fleet in range(self.Number_fleets)]) 
            model.coverage_constraints.add(coverage_sum == 1)
        
        
        # Resource Constraints
        model.resource_constraints = pe.ConstraintList()
        for fleet in range(self.Number_fleets):
            resource_sum = sum([model.RON[f"RON_{station}_{fleet+1}"] for station in self.Stations])
            model.resource_constraints.add(resource_sum == self.fleets["size"][fleet])
        
        
        # Balance Constraints
        model.balance_constraints = pe.ConstraintList()
        
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

                





        model.pprint()
    
    
    
    def return_analysis(self):
        
        self.read_flight_schedule()
        self.read_fleets()
        self.identify_stations()
        self.create_nodes()
        self.create_ground_links()
        self.constraints_matrices()
        self.profit_calculation()
        self.optimize()


        return 

    
        
