import comfit as cf
import numpy as np

qm = cf.QM(1,xRes=101,dx=1)
qm.set_initial_condition_gaussian(width=20)
qm.V_ext = qm.conf_harmonic_potential(0.002)

print(qm.calc_Hamiltonian())