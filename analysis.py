import matplotlib.pyplot as plt
from collections import defaultdict
from qiskit import QuantumCircuit, Aer, execute
from pymongo import MongoClient
from math import pi
from qiskit.circuit.library import QFT
import matplotlib.colors as mcolors
import random

def perform_demand_analysis():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['product']  
    products_collection = db['product'] 

    products = []
    for product in products_collection.find({}, {'name': 1}):
        products.append(product['name'])

   
    initial_demand = {product: 0 for product in products} 
    
    def demand_forecasting_circuit(demand):
       qc = QuantumCircuit(len(products), len(products)) 
       for idx, product in enumerate(products):
            if demand[product]:
                qc.x(idx) 
       qc.append(QFT(len(products)), range(len(products)))
       qc.measure(range(len(products)), range(len(products))) 
       return qc
    demand_data = []
    simulator = Aer.get_backend('qasm_simulator')


    for time_point in range(1, 11):  
        demand = {product: initial_demand[product] + time_point * 5 for product in products}
        qc = demand_forecasting_circuit(demand)
        result = execute(qc, simulator, shots=1024).result()
        counts = result.get_counts(qc)
        demand_data.append({product: counts.get('1'*idx+'0'*(len(products)-idx), 0) for idx, product in enumerate(products)})

    total_demand = defaultdict(int)
    for data in demand_data:
        for product, demand in data.items():
            total_demand[product] += demand

    def generate_colors(num_colors, base_color='#7cc0fc', hue_range=0.1, saturation_range=0.5, value_range=0.5):
        base_rgb = mcolors.hex2color(base_color)
        colors_rgb = []
        for _ in range(num_colors):
            hue = base_rgb[0] + random.uniform(-hue_range, hue_range)
            saturation = max(0, min(1, base_rgb[1] + random.uniform(-saturation_range, saturation_range)))
            value = max(0, min(1, base_rgb[2] + random.uniform(-value_range, value_range)))
            colors_rgb.append((hue, saturation, value))
        return [mcolors.rgb2hex(rgb) for rgb in colors_rgb]


    num_colors_needed = len(total_demand.keys())
    colors_hex = generate_colors(num_colors_needed, base_color='#7cc0fc', hue_range=0.1, saturation_range=0.3, value_range=0.3)


    plt.figure(figsize=(8, 8))
    plt.pie(total_demand.values(), labels=total_demand.keys(),colors=colors_hex, autopct='%1.1f%%', startangle=140) 
    plt.axis('equal')


    plot_path = "static/total_demand_plot.png"
    plt.savefig(plot_path, transparent=True)


    return plot_path

demand = [1, 0, 1, 0] 

