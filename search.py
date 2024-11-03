from qiskit import QuantumCircuit, Aer, execute
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['Warehouse']
collection_pro = db['product']

def fetch_products():
    products = [doc for doc in collection_pro.find()]
    return products

def grover_search(target_product):
    products = fetch_products()
    num_products = len(products)
    num_qubits = num_products.bit_length()

    if num_products == 0:
        return {"error": "No products found in the database"}

    if num_qubits == 0:
        num_qubits = 1  

    if num_products < num_qubits:
        return {"error": "Insufficient number of products to perform the search"}

    oracle = QuantumCircuit(num_qubits)
    for idx, product in enumerate(products):
        if product['code'] == target_product:
            if idx < num_qubits:  
                oracle.x(idx)
    oracle.cz(0, num_qubits-1)
    for idx, product in enumerate(products):
        if product['code'] == target_product:
            if idx < num_qubits:  
                oracle.x(idx)

    diffusion = QuantumCircuit(num_qubits)
    diffusion.h(range(num_qubits))
    diffusion.append(oracle.to_instruction(), range(num_qubits))
    for qubit in range(num_qubits):
        diffusion.x(qubit)
    diffusion.h(num_qubits-1)
    diffusion.append(oracle.to_instruction(), range(num_qubits))
    for qubit in range(num_qubits):
        diffusion.x(qubit)
    diffusion.h(num_qubits-1)

    grover_circuit = QuantumCircuit(num_qubits)
    grover_circuit.h(range(num_qubits))

    iterations = 1 
    for _ in range(iterations):
        grover_circuit.append(oracle.to_instruction(), range(num_qubits))
        grover_circuit.append(diffusion.to_instruction(), range(num_qubits))

    grover_circuit.measure_all()

    simulator = Aer.get_backend('qasm_simulator')
    result = execute(grover_circuit, simulator, shots=1024).result()
    counts = result.get_counts(grover_circuit)

    target_found = any(key[-1] == '1' for key in counts.keys() if key[:-1] == '0' * (num_qubits - 1))

    if target_found:
        return {"target_product": target_product, "target_found": target_found, "product_details": [product for product in products if product['code'] == target_product]}
    else:
        return {"target_product": target_product, "target_found": target_found, "product_details": []}