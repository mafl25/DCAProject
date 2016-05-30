__author__ = 'Manuel'

import math

#  Constants
SILICON_NI = 1.45e10
THERMAL_VOLTAGE = 0.026
TEMPERATURE = 300
EPSILON_NULL = 8.85e-14
EPSILON_SI = 11.7 * EPSILON_NULL
EPSILON_OX = 3.9 * EPSILON_NULL
ELECTRON_CHARGE = 1.6e-19
BOLTZMANN_K = 1.38e-23


class Transistor:
    def __init__(self, name, model, nodes, w, l, transistor_type='N', level=1, uo=800,  tox=100.0,
                 nsub=1e15, nsubsw=2.1e16, nds=1e20, ld=0.8, vto=1.0, plambda=0.0,
                 lens=10, lend=10, kp=None, xj=None, pgamma=None,
                 cox=None, mj=0.5, mjsw=0.5):
        # Circuit Information
        self.id = name
        self.model = model
        if nodes:
            self.drain = nodes[0]
            self.gate = nodes[1]
            self.source = nodes[2]
            self.substrate = nodes[3]
        else:
            self.drain = None
            self.gate = None
            self.source = None
            self.substrate = None

        # Transistor Properties
        self.type = transistor_type
        self.level = level
        self.lens = lens
        self.lend = lend
        self.uo = uo
        self.tox = tox
        self.nsub = nsub
        self.nds = nds
        self.nsubsw = nsubsw
        self.plambda = plambda
        self.vto = vto
        self.mj = mj
        self.mjsw = mjsw

        # Dimensions
        self.w = w
        self.l = l
        self.ld = ld
        self.ars = w * lens * 1e-8
        self.ard = w * lend * 1e-8
        self.ps = (w + 2 * lens) * 1e-4
        self.pd = (w + 2 * lend) * 1e-4

        # Derived values
        self.leff = self.l - 2 * self.ld

        if cox:
            self.cox = cox * 1e-8
        else:
            self.cox = EPSILON_OX / (self.tox * 1e-7)

        if kp:
            self.kp = kp * 1e-6
        else:
            self.kp = uo * self.cox

        self.k = self.kp * w / l

        if pgamma:
            self.pgamma = pgamma
        else:
            self.pgamma = self.calculate_gamma()

        if xj:
            self.xj = xj * 1e-4
        else:
            self.xj = self.calculate_xj()

        self.phi = self.calculate_phi()
        self.pb = self.calculate_pb()
        self.pbsw = self.calculate_pbsw()
        self.cj = self.calculate_cj()
        self.cjsw = self.calculate_cjsw()
        self.cgso = self.calculate_cgo()
        self.cgdo = self.cgso

    def calculate_gamma(self):
        return math.sqrt(2 * EPSILON_SI * ELECTRON_CHARGE * self.nsub) / self.cox

    def calculate_phi(self):
        return 2 * THERMAL_VOLTAGE * math.log(SILICON_NI / self.nsub)

    def calculate_pb(self):
        return THERMAL_VOLTAGE * math.log(self.nsub * self.nds / SILICON_NI ** 2)

    def calculate_pbsw(self):
        return THERMAL_VOLTAGE * math.log(self.nsubsw * self.nds / SILICON_NI ** 2)

    def calculate_vt(self, vsb):
        vt = self.vto + self.pgamma * (math.sqrt(math.fabs(-self.phi + vsb)) - math.sqrt(math.fabs(self.phi)))
        return vt

    def calculate_xj(self):
        x = 2 * EPSILON_SI * self.pb / ELECTRON_CHARGE
        y = (self.nsub + self.nds) / (self.nsub * self.nds)
        return math.sqrt(x * y)

    def calculate_keq(self, v1, v2):
        v1 = -v1
        v2 = -v2
        x = math.sqrt(self.pb - v2) - math.sqrt(self.pb - v1)
        y = -2 * math.sqrt(self.pb) / (v2 - v1)
        return y * x

    def calculate_keqsw(self, v1, v2):
        v1 = -v1
        v2 = -v2
        x = math.sqrt(self.pbsw - v2) - math.sqrt(self.pbsw - v1)
        y = -2 * math.sqrt(self.pbsw) / (v2 - v1)
        return y * x

    def calculate_cj(self):
        x = EPSILON_SI * ELECTRON_CHARGE / (2 * self.pb)
        y = self.nsub * self.nds / (self.nsub + self.nds)
        return math.sqrt(x * y)

    def calculate_cjsw(self):
        x = EPSILON_SI * ELECTRON_CHARGE / (2 * self.pbsw)
        y = self.nsubsw * self.nds / (self.nsubsw + self.nds)
        return self.xj * math.sqrt(x * y)  # Add xj somehow

    def calculate_cgo(self):
        return self.cox * self.ld * 1e-4

    def calculate_cdb(self, v1, v2):
        area = self.ard + self.w * self.xj * 1e-4
        return area * self.cj * self.calculate_keq(v1, v2) + self.pd * self.cjsw * self.calculate_keqsw(v1, v2)

    def calculate_cg(self):
        w = self.w * 1e-4
        l = self.l * 1e-4
        ld = self.ld * 1e-4
        return self.cox * w * (l + 2 * ld) + 2 * self.cox * w * ld

    def spice_print(self, print_return):
        spice_string = self.id + ' ' + self.drain + ' ' + self.gate + ' ' + self.source + ' ' + self.substrate + ' '
        if self.type == 'N':
            fet_type = 'NMOS '
        elif self.type == 'P':
            fet_type = 'PMOS '
        else:
            fet_type = 'ERROR '
        spice_string += self.model + ' L=' + str(self.l) + 'U W=' + str(self.w) + 'U AS=' + str(self.ars * 1e8)
        spice_string += 'P PS=' + str(self.ps * 1e4) + 'U AD=' + str(self.ard * 1e8) + 'P PD=' + str(self.pd * 1e4)
        spice_string += 'U\n.MODEL ' + self.model + ' ' + fet_type + '(VTO=' + str(self.vto) + ' KP='
        spice_string += '{:.2f}'.format(self.kp * 1e6) + 'U'
        spice_string += ' GAMMA=' + '{:.2f}'.format(self.pgamma) + ' PHI={:.2f}'.format(abs(self.phi))
        spice_string += ' PB={:.3f}'.format(self.pb) + ' CJ={:.2E}'.format(self.cj * 1e4)
        spice_string += ' CJSW={:.2E}'.format(self.cjsw * 1e2) + ' CGSO={:.2E}'.format(self.cgso * 1e2)
        spice_string += ' CGDO={:.2E}'.format(self.cgdo * 1e2) + ' MJ={:.2f}'.format(self.mj)
        spice_string += ' MJSW={:.2f}'.format(self.mjsw) + ' LEVEL=' + str(self.level) + ')'

        if print_return:
            print(spice_string)
        else:
            return spice_string


if __name__ == "__main__":
    t1 = Transistor('M1', "NM1", ['VDD', '1', '0', '0'], 5, 2, transistor_type='N', nsub=2e15,
                    nsubsw=4e16, nds=1e19, tox=45, xj=1, lend=10, lens=10)
    t1.spice_print(True)
    print(t1.calculate_cdb(0.5, 5))
