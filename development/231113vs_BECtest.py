import comfit as cf
import numpy as np
import matplotlib.pyplot as plt

bec = cf.BEC(2,xRes=51,yRes=51)
bec.conf_insert_vortex_dipole()
bec.evolve_relax_BEC(100)

rho = bec.calc_vortex_density()

bec.plot_field(rho)
plt.show()