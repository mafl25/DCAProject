__author__ = 'Manuel'


import Transistor
import math
import CircuitRead

VCC = 'VCC'
GND = 'GND'


class Inverter:
    def __init__(self, input, output, name, tp, tn):
        self.id = name
        self.input = input
        self.output = output
        self.nodes_tp = [output, input, VCC, VCC]
        self.nodes_tn = [output, input, GND, GND]
        self.tp = Transistor.Transistor('M' + self.id + 'TP', tp.model, self.nodes_tp, tp.w, tp.l, 'P', tp.level,
                                         tp.uo, tp.tox, tp.nsub, tp.nsubsw, tp.nds, tp.ld, tp.vto, tp.plambda, tp.lens,
                                         tp.lend, tp.kp * 1e6, tp.xj * 1e4, tp.pgamma, tp.cox * 1e8, tp.mj,
                                         tp.mjsw)
        self.tn = Transistor.Transistor('M' + self.id + 'TN', tn.model, self.nodes_tn, tn.w, tn.l, 'N', tn.level,
                                         tn.uo, tn.tox, tn.nsub, tn.nsubsw, tn.nds, tn.ld, tn.vto, tn.plambda, tn.lens,
                                         tn.lend, tn.kp * 1e6, tn.xj * 1e4, tn.pgamma, tn.cox * 1e8, tn.mj,
                                         tn.mjsw)
    def get_eq_wln(self):
        return self.tn.w / self.tn.l

    def get_eq_wlp(self):
        return self.tp.w / self.tp.l

    def calculate_tphl(self, vdd, cload):
        v_dif = vdd - self.tn.vto
        v_div = self.tn.vto / v_dif
        f_div = cload / (self.get_eq_wln() * self.tn.uo * self.tn.cox * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vdd - 1))

    def calculate_tplh(self, vdd, cload):
        v_dif = vdd - abs(self.tp.vto)
        v_div = abs(self.tp.vto) / v_dif
        f_div = cload / (self.get_eq_wlp() * self.tp.uo * self.tp.cox * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vdd - 1))

    def spice_print(self):
        spice_string = self.tp.spice_print(False) + '\n' + self.tn.spice_print(False)
        print(spice_string)


class Nand:
    def __init__(self, a, b, output, name, tp, tn):
        self.an = None
        self.bn = None
        self.outputn = None

        self.id = name
        self.a = a
        self.b = b
        self.output = output
        self.nodes_tp1 = [output, a, VCC, VCC]
        self.nodes_tp2 = [output, b, VCC, VCC]
        self.nodes_tn1 = [output, a, self.id + '3N', GND]
        self.nodes_tn2 = [self.id + '3N', b, GND, GND]
        self.tp1 = Transistor.Transistor('M' + self.id + 'TP1', tp.model, self.nodes_tp1, tp.w, tp.l, 'P', tp.level,
                                         tp.uo, tp.tox, tp.nsub, tp.nsubsw, tp.nds, tp.ld, tp.vto, tp.plambda, tp.lens,
                                         tp.lend, tp.kp * 1e6, tp.xj * 1e4, tp.pgamma, tp.cox * 1e8, tp.mj,
                                         tp.mjsw)
        self.tp2 = Transistor.Transistor('M' + self.id + 'TP2', tp.model, self.nodes_tp2, tp.w, tp.l, 'P', tp.level,
                                         tp.uo, tp.tox, tp.nsub, tp.nsubsw, tp.nds, tp.ld, tp.vto, tp.plambda, tp.lens,
                                         tp.lend, tp.kp * 1e6, tp.xj * 1e4, tp.pgamma, tp.cox * 1e8, tp.mj,
                                         tp.mjsw)
        self.tn1 = Transistor.Transistor('M' + self.id + 'TN1', tn.model, self.nodes_tn1, tn.w, tn.l, 'N', tn.level,
                                         tn.uo, tn.tox, tn.nsub, tn.nsubsw, tn.nds, tn.ld, tn.vto, tn.plambda, tn.lens,
                                         tn.lend, tn.kp * 1e6, tn.xj * 1e4, tn.pgamma, tn.cox * 1e8, tn.mj,
                                         tn.mjsw)
        self.tn2 = Transistor.Transistor('M' + self.id + 'TN2', tn.model, self.nodes_tn2, tn.w, tn.l, 'N', tn.level,
                                         tn.uo, tn.tox, tn.nsub, tn.nsubsw, tn.nds, tn.ld, tn.vto, tn.plambda, tn.lens,
                                         tn.lend, tn.kp * 1e6, tn.xj * 1e4, tn.pgamma, tn.cox * 1e8, tn.mj,
                                         tn.mjsw)

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)

    def calculate_wln_inverter_eq(self, vdd, cload, delay):
        v_dif = vdd - self.tn1.vto
        v_div = self.tn1.vto / v_dif
        f_div = cload / (delay * self.tn1.uo * self.tn1.cox * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vdd - 1))

    def calculate_wlp_inverter_eq(self, vdd, cload, delay):
        v_dif = vdd - abs(self.tp1.vto)
        v_div = abs(self.tp1.vto) / v_dif
        f_div = cload / (delay * self.tp1.uo * self.tp1.cox * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vdd - 1))

    def get_eq_wln(self):
        return 0.5 * self.tn1.w / self.tn1.l

    def get_eq_wlp(self):
        return self.tp1.w / self.tp1.l

    def calculate_int_loac_c(self, v1, v2):
        cload = 2 * self.tp1.calculate_cdb(v1, v2) + 3 * self.tn1.calculate_cdb(v1, v2)
        cload += self.tp1.calculate_cg() + self.tn1.calculate_cg()
        return cload

    def calculate_tphl(self, vcc, cload):
        cload += self.calculate_int_loac_c(vcc, vcc * 0.5)
        v_dif = vcc - self.tn1.vto
        v_div = self.tn1.vto / v_dif
        f_div = cload / (self.get_eq_wln() * self.tn1.kp * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vcc - 1))

    def calculate_tplh(self, vcc, cload):
        cload += self.calculate_int_loac_c(0, vcc * 0.5)
        v_dif = vcc - abs(self.tp1.vto)
        v_div = abs(self.tp1.vto) / v_dif
        f_div = cload / (self.get_eq_wlp() * self.tp1.kp * v_dif)
        return f_div * (2 * v_div + math.log(4 * v_dif / vcc - 1))

    def spice_print(self):
        spice_string = self.tp1.spice_print(False) + '\n' + self.tp2.spice_print(False) + '\n'
        spice_string += self.tn1.spice_print(False) + '\n' + self.tn2.spice_print(False)
        print(spice_string)

    def calculate_delay(self, vcc, c):
        tlh = self.calculate_tplh(vcc, c)
        thl = self.calculate_tphl(vcc, c)
        pd = (tlh + thl) / 2
        return pd

    def calculate_gc(self):
        return self.tp1.calculate_cg() + self.tn1.calculate_cg()

    def set_nodes(self, a, b, out):
        self.an = a
        self.bn = b
        self.outputn = out


class NANDAnd:
    def __init__(self, a, b, output, name, tp, tn):
        self.an = None
        self.bn = None
        self.outputn = None

        self.id = name
        self.gate1 = Nand(a, b, name + 'IN', name + 'G1', tp, tn)
        self.gate2 = Nand(name + 'IN', name + 'IN', output, name + 'G2', tp, tn)

    def spice_print(self):
        self.gate1.spice_print()
        self.gate2.spice_print()

    def calculate_delay(self, vcc, c):
        gate2_c = 2 * self.gate2.calculate_gc()
        gate1_delay = self.gate1.calculate_delay(vcc, gate2_c)
        gate2_delay = self.gate2.calculate_delay(vcc, c)
        return gate1_delay + gate2_delay

    def calculate_gc(self):
        return self.gate1.calculate_gc()

    def set_nodes(self, a, b, out):
        self.an = a
        self.bn = b
        self.outputn = out

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)


class NANDOr:
    def __init__(self, a, b, output, name, tp, tn):
        self.an = None
        self.bn = None
        self.outputn = None

        self.id = name
        self.gate1 = Nand(a, a, name + 'IN1', name + 'G1', tp, tn)
        self.gate2 = Nand(b, b, name + 'IN2', name + 'G2', tp, tn)
        self.gate3 = Nand(name + 'IN2', name + 'IN1', output, name + 'G3', tp, tn)

    def spice_print(self):
        self.gate1.spice_print()
        self.gate2.spice_print()
        self.gate3.spice_print()

    def set_nodes(self, a, b, out):
        self.an = a
        self.bn = b
        self.outputn = out

    def calculate_gc(self):
        return 2 * self.gate1.calculate_gc()

    def calculate_delay(self, vcc, c):
        gate3_c = self.gate3.calculate_gc()
        gate1_delay = self.gate1.calculate_delay(vcc, gate3_c)
        gate3_delay = self.gate3.calculate_delay(vcc, c)
        return gate1_delay + gate3_delay

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)


class NANDxor:
    def __init__(self, a, b, output, name, tp, tn):
        self.an = None
        self.bn = None
        self.outputn = None

        self.id = name
        self.gate1 = Nand(a, b, name + 'IN1', name + 'G1', tp, tn)
        self.gate2 = Nand(a, name + 'IN1', name + 'IN2', name + 'G2', tp, tn)
        self.gate3 = Nand(b, name + 'IN1', name + 'IN3', name + 'G3', tp, tn)
        self.gate4 = Nand(name + 'IN3', name + 'IN2', output, name + 'G4', tp, tn)

    def spice_print(self):
        self.gate1.spice_print()
        self.gate2.spice_print()
        self.gate3.spice_print()
        self.gate4.spice_print()

    def set_nodes(self, a, b, out):
        self.an = a
        self.bn = b
        self.outputn = out

    def calculate_gc(self):
        return 2 * self.gate1.calculate_gc()

    def calculate_delay(self, vcc, c):
        gate2_3_c = self.gate2.calculate_gc() + self.gate3.calculate_gc()
        gate1_delay = self.gate1.calculate_delay(vcc, gate2_3_c)
        gate4_c = self.gate4.calculate_gc()
        gate2_delay = self.gate1.calculate_delay(vcc, gate4_c)
        gate4_delay = self.gate4.calculate_delay(vcc, c)
        return gate1_delay + gate2_delay + gate4_delay

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)


def nand_inverter(input, output, name, tp, tn):
    return Nand(input, input, output, name, tp, tn)


if __name__ == "__main__":
    tp = Transistor.Transistor(None, "PM1", None, 2*18.6, 1.2, transistor_type='P', nsub=1e15, lens=3.5, lend=3.9,
                               nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=-1.0, ld=0.25, uo=1000, cox=6, level=3)
    tn = Transistor.Transistor(None, "NM1", None, 2*4.7, 1.2, transistor_type='N', nsub=1e15, lens=3.5, lend=3.9,
                               nsubsw=2.1e16, nds=1e20, tox=60, xj=0.8, vto=0.8, ld=0.25, uo=1000, cox=12, level=3)
    nand = Nand('A', 'NOTA', 'B', 'NAND1', tp, tn)
    nand.spice_print()
    inv1 = nand_inverter('A', 'NOTA', 'INV1', tp, tn)
    inv2 = nand_inverter('B', 'OUT', 'INV2', tp, tn)

    inv1.spice_print()
    #inv2.spice_print()

    #print(nand.calculate_delay(5, 300e-15))
    print(inv1.calculate_delay(5, nand.tp1.calculate_cg() + nand.tn1.calculate_cg()))
    #print(inv2.calculate_delay(3, 300e-15))
    iv = Inverter('A', 'OUT', 'INV1', tp, tn)
