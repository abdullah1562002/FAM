import FAM
import pandas as pd


# Create an instance of the class
analyzer = FAM.FAM("Time Schedule.xlsx")

# Perform operations
print(analyzer.return_analysis())



#Node = [{'Node': 1, 'Station': 'JFK', 'Inbound': ['RON_JFK'], 'Outbound': [1, 'y(1-2)']}, {'Node': 2, 'Station': 'JFK', 'Inbound': ['y(1-2)', 2], 'Outbound': [3, 'y(2-3)']}, {'Node': 3, 'Station': 'JFK', 'Inbound': ['y(2-3)', 4], 'Outbound': ['RON_JFK']}, {'Node': 4, 'Station': 'ORD', 'Inbound': ['RON_ORD', 1], 'Outbound': [9, 'y(4-5)']}, {'Node': 5, 'Station': 'ORD', 'Inbound': ['y(4-5)', 13], 'Outbound': [2, 14, 'y(5-6)']}, {'Node': 6, 'Station': 'ORD', 'Inbound': ['y(5-6)', 5], 'Outbound': [6, 'y(6-7)']}, {'Node': 7, 'Station': 'ORD', 'Inbound': ['y(6-7)', 10], 'Outbound': [15, 11, 4, 'y(7-8)']}, {'Node': 8, 'Station': 'ORD', 'Inbound': ['y(7-8)', 3, 7], 'Outbound': [8, 'y(8-9)']}, {'Node': 9, 'Station': 'ORD', 'Inbound': ['y(8-9)', 16, 12], 'Outbound': ['RON_ORD']}, {'Node': 10, 'Station': 'SEA', 'Inbound': ['RON_SEA'], 'Outbound': [5, 'y(10-11)']}, {'Node': 11, 'Station': 'SEA', 'Inbound': ['y(10-11)', 6], 'Outbound': [7, 'y(11-12)']}, {'Node': 12, 'Station': 'SEA', 'Inbound': ['y(11-12)', 8], 'Outbound': ['RON_SEA']}, {'Node': 13, 'Station': 'BOS', 'Inbound': ['RON_BOS', 9], 'Outbound': [10, 'y(13-14)']}, {'Node': 14, 'Station': 'BOS', 'Inbound': ['y(13-14)', 11], 'Outbound': [12, 'RON_BOS']}, {'Node': 15, 'Station': 'LAX', 'Inbound': ['RON_LAX'], 'Outbound': [13, 'y(15-16)']}, {'Node': 16, 'Station': 'LAX', 'Inbound': ['y(15-16)', 14, 15], 'Outbound': [16, 'RON_LAX']}]

