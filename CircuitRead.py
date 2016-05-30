__author__ = 'Manuel'

import Transistor
import Gates

prefix = {'y': 1e-24,  # yocto
           'z': 1e-21,  # zepto
           'a': 1e-18,  # atto
           'f': 1e-15,  # femto
           'p': 1e-12,  # pico
           'n': 1e-9,   # nano
           'u': 1e-6,   # micro
           'm': 1e-3,   # mili
           'c': 1e-2,   # centi
           'd': 1e-1,   # deci
           'k': 1e3,    # kilo
           'M': 1e6,    # mega
           'G': 1e9,    # giga
           'T': 1e12,   # tera
           'P': 1e15,   # peta
           'E': 1e18,   # exa
           'Z': 1e21,   # zetta
           'Y': 1e24,   # yotta
    }


class Node:
    def __init__(self, name):
        self.name = name
        self.output = None
        self.inputs = []
        self.capacitance = 0

    def set_output(self, gate):
        self.output = gate

    def add_inputs(self, gate):
        self.inputs.append(gate)

    def print(self):
        print("\nNode = " + self.name)
        if self.output:
            print("Output = " + self.output.id)
        if len(self.inputs):
            print("Inputs = ", end="")
            for gate in self.inputs:
                print(gate.id, end=" ")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class NodeContainer:
    def __init__(self):
        self.nodes = []
        self.inputs = []
        self.outputs = []

    def add_node(self, node):
        node_found = False
        for n in self.nodes:
            if n.name == node:
                return n
        if not node_found:
            n = Node(node)
            self.nodes.append(n)
            return n

    def print(self):
        for node in self.nodes:
            node.print()

    def organize(self):
        for node in self.nodes:
            if not node.output:
                self.inputs.append(node)
            if not len(node.inputs):
                self.outputs.append(node)

    def get_next_nodes(self, node, path, storage):
        if len(node.inputs):
            if not path:
                path = []
            paths = [path[:] for i in range(len(node.inputs))]
            for i, gate in enumerate(node.inputs):
                paths[i].append(gate)
                self.get_next_nodes(gate.outputn, paths[i], storage)
        else:
            storage.append(path)

    def calculate_paths(self):
        self.organize()
        paths = []
        for node in self.inputs:
            storage = []
            self.get_next_nodes(node, None, storage)
            paths.append(storage)
        return paths

    def organize_by_outputs(self, paths):
        output_paths = []
        for output_node in self.outputs:
            output_path = []
            for input in paths:
                for path in input:
                    if path[-1] == output_node.output:
                        output_path.append(path)
            output_paths.append(output_path)
        return output_paths


def read_circuit(address, tp, tn, nodes):
    voltage = None
    gates = []

    with open(address, 'r') as out_file:
        line = out_file.readline()
        while line:
            line = line.split()
            if line[0] == "vcc":
                voltage = float(line[1])
            elif line[0] == 'nand':
                in1 = nodes.add_node(line[1])
                in2 = nodes.add_node(line[2])
                out1 = nodes.add_node(line[3])

                gates.append(Gates.Nand(line[1], line[2], line[3], line[4], tp, tn))

                in1.add_inputs(gates[-1])
                in2.add_inputs(gates[-1])
                out1.set_output(gates[-1])

                gates[-1].set_nodes(in1, in2, out1)

            elif line[0] == 'inv':
                in1 = nodes.add_node(line[1])
                out1 = nodes.add_node(line[2])

                gates.append(Gates.nand_inverter(line[1], line[2], line[3], tp, tn))

                in1.add_inputs(gates[-1])
                out1.set_output(gates[-1])

                gates[-1].set_nodes(in1, in1, out1)

            elif line[0] == 'and':
                in1 = nodes.add_node(line[1])
                in2 = nodes.add_node(line[2])
                out1 = nodes.add_node(line[3])

                gates.append(Gates.NANDAnd(line[1], line[2], line[3], line[4], tp, tn))

                in1.add_inputs(gates[-1])
                in2.add_inputs(gates[-1])
                out1.set_output(gates[-1])

                gates[-1].set_nodes(in1, in2, out1)

            elif line[0] == 'or':
                in1 = nodes.add_node(line[1])
                in2 = nodes.add_node(line[2])
                out1 = nodes.add_node(line[3])

                gates.append(Gates.NANDOr(line[1], line[2], line[3], line[4], tp, tn))

                in1.add_inputs(gates[-1])
                in2.add_inputs(gates[-1])
                out1.set_output(gates[-1])

                gates[-1].set_nodes(in1, in2, out1)

            elif line[0] == 'xor':
                in1 = nodes.add_node(line[1])
                in2 = nodes.add_node(line[2])
                out1 = nodes.add_node(line[3])

                gates.append(Gates.NANDxor(line[1], line[2], line[3], line[4], tp, tn))

                in1.add_inputs(gates[-1])
                in2.add_inputs(gates[-1])
                out1.set_output(gates[-1])

                gates[-1].set_nodes(in1, in2, out1)

            elif line[0].startswith('c'):
                n = nodes.add_node(line[1])
                if not line[2].isnumeric():
                    factor = prefix[line[2][-1]]
                    n.capacitance = float(line[2][:-1]) * factor
                else:
                    n.capacitance = float(line[2])

            line = out_file.readline()
    return voltage, gates


def path_delays(vcc, path):
    total_delay = 0
    for gate in path:
        gate_capacitance = 0
        for inputs in gate.outputn.inputs:
            gate_capacitance += inputs.calculate_gc()
        total_delay += gate.calculate_delay(vcc, gate_capacitance + gate.outputn.capacitance)
    return total_delay

if __name__ == "__main__":
    filepath = '''C:/Users/Manuel/Desktop/test2.txt'''
    tp = Transistor.Transistor(None, "PM1", None, 5*18.6, 1.2, transistor_type='P', nsub=1e15, lens=3.5, lend=3.9,
                               nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=-1.0, ld=0.25, uo=1000, cox=6, level=3)
    tn = Transistor.Transistor(None, "NM1", None, 5*4.7, 1.2, transistor_type='N', nsub=1e15, lens=3.5, lend=3.9,
                               nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=0.8, ld=0.25, uo=1000, cox=12, level=3)
    new_nodes = NodeContainer()
    voltage, gates = read_circuit(filepath, tp, tn, new_nodes)
    paths = new_nodes.calculate_paths()

    opaths = new_nodes.organize_by_outputs(paths)
    for i, output in enumerate(opaths):
        print(new_nodes.outputs[i])
        delays = []
        for path in output:
            print(path)
            delays.append(path_delays(voltage, path))
        print(delays)
        print('')

    for gate in gates:
        gate.spice_print()

