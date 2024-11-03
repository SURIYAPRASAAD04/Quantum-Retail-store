from qiskit_algorithms.utils import algorithm_globals
from qiskit.circuit.library import ZFeatureMap
from pymongo import MongoClient
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT
import numpy as np
import matplotlib.pyplot as plt
import os
from math import pi
from pymongo import MongoClient

def fetch_initial_demand_from_database(products):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["product"] 
    collection = db["product"]  
    
    initial_demand = {}

    for product in products:
        demand_data = collection.find_one({"product_name": product})
        if demand_data:
            initial_demand[product] = demand_data["demand"]  
        else:
            initial_demand[product] = []  
    
    client.close()
    return initial_demand


def quan():
    num_qubits = 30
    products = ["Goodday","lays","Milk","Coca-Cola","Apple","Chips Ahoy"]
    
    initial_demand = {
        "Goodday": [201, 205, 110, 50, 22, 22, 23, 30, 112, 145, 90, 55, 60, 65, 10, 75, 28, 90, 210, 125, 120, 67, 170, 167, 130, 35, 78, 121, 32, 88],
        "lays": [20, 12, 13, 15, 78, 45, 56, 55, 60, 65, 17, 75, 76, 56, 110, 95, 65, 25, 21, 15, 20, 25, 30, 35, 24, 45, 25, 55, 60, 65],
        "Milk": [90, 92, 94, 96, 98, 100, 102, 204, 16, 18, 0, 12, 41, 61, 18, 10, 12, 124, 126, 128, 230, 132, 90, 16, 89, 40, 42, 44, 146, 99],
        "Coca-Cola": [20, 85, 38, 95, 40, 95, 150, 155, 60, 95, 77, 76, 70, 105, 190, 51, 90, 135, 110, 89, 90, 125, 130, 190, 140, 145, 67, 89, 160, 175],
        "Apple": [123, 26, 99, 82, 75, 98, 81, 84, 47, 50, 23, 56, 89, 92, 65, 68, 71, 170, 177, 60, 83, 98, 89, 78, 25, 38, 101, 79, 67, 110],
        "Chips Ahoy": [45, 17, 9, 15, 17, 10, 103, 99, 69, 89, 75, 86, 81, 14, 78, 190, 93, 39, 79, 95, 140, 67, 56, 90, 91, 6, 46, 26, 19, 22],
    }

    demand_data = []
    days = range(1, 31)  
    simulator = Aer.get_backend('qasm_simulator')
    shots = 1024
    
    for time_point in days:
        demand = {product: [initial_demand[product][0] + time_point * 5] for product in products}
        qc = demand_forecasting_circuit(demand)
        result = execute(qc, simulator, shots=shots).result()
        counts = result.get_counts(qc)
        demand_data.append({product: counts.get('1'*idx+'0'*(len(products)-idx), 0) for idx, product in enumerate(products)})
    
    
    total_demand = {product: sum([data[product] for data in demand_data]) for product in products}
    highest_demand_product = max(total_demand, key=total_demand.get)
    

    plt.figure(figsize=(10, 6))
    for idx, prod in enumerate(products):
     if prod is not None:
        plt.plot(np.arange(1, num_qubits + 1), initial_demand[prod], marker='o', label=prod)

    plt.xlabel('Day')
    plt.ylabel('Number of Products Sold')
    plt.title('Demand Forecasting')
    plt.legend()
    plt.grid(True)
    image_path = 'static/plot.png'
    plt.savefig(image_path, transparent=True)
    plt.close()

    result = f"The product with the highest demand is {highest_demand_product}."
    return result, image_path

def demand_forecasting_circuit(demand):
    num_qubits = len(demand)
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    for idx, product in enumerate(demand):
        if demand[product]:
            qc.h(idx)
    
    qc.append(QFT(num_qubits), range(num_qubits))
    
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc

"""demand = [1, 0, 1, 0] 
circuit = demand_forecasting_circuit(demand)
print(circuit)
circuit.draw(output='mpl')"""

