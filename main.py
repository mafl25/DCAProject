__author__ = 'Manuel'

import CircuitRead
import Transistor


filepath = '''C:/Users/Manuel/Desktop/test1.txt'''
tp = Transistor.Transistor(None, "PM1", None, 5*18.6, 1.2, transistor_type='P', nsub=1e15, lens=3.5, lend=3.9,
                           nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=-1.0, ld=0.25, uo=1000, cox=6, level=3)
tn = Transistor.Transistor(None, "NM1", None, 5*4.7, 1.2, transistor_type='N', nsub=1e15, lens=3.5, lend=3.9,
                           nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=0.8, ld=0.25, uo=1000, cox=12, level=3)
new_nodes = CircuitRead.NodeContainer()
voltage, gates = CircuitRead.read_circuit(filepath, tp, tn, new_nodes)

paths = new_nodes.calculate_paths()
opaths = new_nodes.organize_by_outputs(paths)

for i, output in enumerate(opaths):
    print(new_nodes.outputs[i])
    delays = []
    for path in output:
        print(path)
        delays.append(CircuitRead.path_delays(voltage, path))
    print(max(delays))
    print('')

for gate in gates:
    gate.spice_print()