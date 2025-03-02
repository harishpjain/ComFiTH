import comfit as cf
import matplotlib.pyplot as plt

pfc = cf.PFCtri(20,10)
print(pfc.a0)
print(pfc.q)

eta = pfc.conf_insert_dislocation()
pfc.calc_from_amplitudes(eta)

#pfc.plot_complex_field(eta[0])
#fig = plt.figure()
#ax = plt.gcf().add_subplot(111)

#We are in business
pfc.plot_field(pfc.psi)
#plt.colorbar(plt.gci())
plt.show()