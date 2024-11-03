from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit_optimization import QuadraticProgram
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

def calculate_area(length, breadth):
    return length * breadth

incoming_box_area = calculate_area(10, 10)
incoming_box_weight = 50

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

def one():
    left_stackshelf_area = {
        "Ar1c1r1": 480,
        "Ar1c1r2": 180,
        "Ar1c1r3": 320,
        "Ar1c1r4": 180,
        "Ar1c1r5": 0
    }

    max_weight_capacity = {
        "Ar1c1r1": 100,
        "Ar1c1r2": 200,
        "Ar1c1r3": 300,
        "Ar1c1r4": 400,
        "Ar1c1r5": 500
    }

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    '''print("\nQuantum Circuit:")
    print(qc)'''

    selected_stack_shelf = None
    selected_stack_shelf_area = float('inf')
    qp = QuadraticProgram()
    for shelf in left_stackshelf_area:
        qp.binary_var(f'x_{shelf}')

    for shelf, area in left_stackshelf_area.items():
        if area >= incoming_box_area:
            for shelf, area in left_stackshelf_area.items():
              if area >= incoming_box_area:
                qp.minimize(area)
                if area < selected_stack_shelf_area:

                  if incoming_box_weight <= max_weight_capacity[shelf]:

                    optimizer = COBYLA()
                    for shelf, weight_capacity in max_weight_capacity.items():

                      weight = 0 if shelf not in left_stackshelf_area else incoming_box_weight
                      qp.linear_constraint(linear={'x_' + shelf: 1}, sense='LE', rhs=weight_capacity - weight)
                      '''qaoa = QAOA(optimizer=optimizer)
                      result = qaoa.solve(qp)'''
                      selected_stack_shelf = shelf
                      selected_stack_shelf_area = area

    if selected_stack_shelf is not None:
        print("Stack No :One")
        print("Selected Stack Shelf:", selected_stack_shelf)
    else:
        print("none")

one()