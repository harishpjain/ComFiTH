import numpy as np
from comfit.core.base_system import BaseSystem


class BEC(BaseSystem):
    def __init__(self, dimension, **kwargs):
        """
        Initializes a system to simulate a Bose-Einstein Condensate using the Gross-Pitaevskii equation.

        Parameters:
        - dimension : int
            The dimension of the system.
        - x_resolution : int
            The resolution along the x-axis.
        - kwargs : dict, optional
            Optional keyword arguments to set additional parameters.

        Returns:
        - BEC object
            The system object representing the BEC simulation.

        Example:
        bec = BEC(3, 100, dissipation_factor=0.5)
        Creates a BEC system with 3 dimensions and an x-resolution of 100. The dissipation factor is set to 0.5.
        """

        # First initialize the BaseSystem class
        super().__init__(dimension, **kwargs)

        # Type of the system
        self.psi = None
        self.psi_f = None
        self.type = 'BEC'

        # Default simulation parameters
        self.gamma = 0.1  # Dissipation (gamma)
        self.V_ext = 0  # External potential

        # If there are additional arguments provided, set them as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Initial conditions
    def set_initial_condition_disordered(self, noise_strength=0.01):
        """
        Sets disordered initial condition for the BEC with some thermal flcutiations

        :param noise_strength:
        :return:
        """

        if self.dim==1:
            self.psi = np.random.rand(self.xRes) - 0.5 + \
                       1j * np.random.rand(self.xRes) - 0.5j

        elif self.dim==2:
            self.psi = np.random.rand(self.xRes, self.yRes)-0.5 + \
                       1j*np.random.rand(self.xRes, self.yRes)-0.5j

        elif self.dim==3:
            self.psi = np.random.rand(self.xRes, self.yRes,self.zRes) - 0.5 + \
                       1j * np.random.rand(self.xRes, self.yRes,self.zRes) - 0.5j
        else:
            raise Exception("Code for this dimension has not yet been implemented.")

        self.psi = noise_strength*self.psi
        self.psi_f = np.fft.fftn(self.psi)

    def set_harmonic_potential(self,R_tf):
        """
        Set the external potential to a harmonic trap with R_tf being the thomas fermi radius
        :param R_tf:
        :return:
        """
        trapping_strength = 1 / (R_tf ** 2)
        if self.dim ==1:
            return  trapping_strength*(self.x -self.xmid )**2
        if self.dim == 2:
            return trapping_strength*(((self.x-self.xmid)**2).reshape(self.xRes, 1)
                                         +((self.y-self.ymid)**2).reshape(1, self.yRes) )
        if self.dim == 3:
            return trapping_strength * (((self.x - self.xmid) ** 2).reshape(self.xRes, 1,1)
                                           + ((self.y - self.ymid) ** 2).reshape(1, self.yRes,1)
                                           +((self.z - self.zmid) ** 2).reshape(1, 1,self.zRes) )

    def set_initial_condition_Thomas_Fermi(self):
        """
        Finds the Thomas_Fermi ground state of a given potential
        must be precided by an energy relaxation to find the true ground state
        :return:
        """
        self.psi = np.emath.sqrt(1-self.V_ext)
        self.psi[self.V_ext > 1] = 0
        self.psi_f = np.fft.fftn(self.psi)

    def gaussian_stiring_potential(self,size,strength,position):

        if self.dim ==1:
            return strength*np.exp( -(self.x -position[0])**2/size**2 )

        if self.dim == 2:
            return strength*np.exp(-(((self.x-position[0])**2).reshape(self.xRes, 1)
                                         + ((self.y-position[1])**2).reshape(1, self.yRes)) /size**2 )
        if self.dim == 3:
            return strength * np.exp(-(((self.x - position[0]) ** 2).reshape(self.xRes, 1,1)
                                           + ((self.y - position[1]) ** 2).reshape(1, self.yRes,1)
                                           +((self.z - position[2]) ** 2).reshape(1, 1,self.zRes))/size**2 )

    #Time evolution
    def evolve_dGPE(self,number_of_steps):

        integrating_factors_f = self.calc_evolution_integrating_factors_dGPE_f()

        for n in range(number_of_steps):
            self.psi, self.psi_f = self.evolve_ETDRK2_loop(integrating_factors_f, self.psi, self.psi_f)



    def evolve_relax_BEC(self,number_of_steps):
        """
        Evolves the BEC in 'imaginary time' to reach a stable (low free energy state).
        :param number_of_steps:
        :return:
        """
        gamma0 = self.gamma

        self.gamma=1-1j

        self.evolve_dGPE(number_of_steps)

        self.gamma=gamma0



    #Calculation functions
    def calc_evolution_integrating_factors_dGPE_f(self):

        k2 = self.calc_k2()

        omega_f = (1j + self.gamma) * (1 - 1 / 2 * k2)

        integration_factors_f = [0,0,0]

        integration_factors_f[0] = np.exp(omega_f * self.dt)
        If1 = integration_factors_f[0]

        integration_factors_f[1] = (If1 - 1) / omega_f

        integration_factors_f[2] = 1 / (self.dt * omega_f**2) * (If1 - 1 - omega_f * self.dt)

        # for i in range(3):
        #     if self.dim == 1:
        #         integration_factors_f[i][0]=0
        #     elif self.dim == 2:
        #         integration_factors_f[i][0,0]=0
        #     elif self.dim == 3:
        #         integration_factors_f[i][0,0,0]=0

        return integration_factors_f

    def calc_nonlinear_evolution_term_f(self,psi):
        psi2 = np.abs(psi)**2

        return np.fft.fftn((1j+self.gamma)*(-self.V_ext-psi2)*psi)


    def position_update_circular_stirrer_2D(self,stirrer_radius,t,stirrer_velocity):
        """
        Gives the position of a stiring potential at a given time
        :param stirrer_radius:
        :param t:
        :param stirrer_velocity:
        :return:
        """
        freq = stirrer_velocity/stirrer_radius
        posx = self.xmid + stirrer_radius*np.cos(freq*t)
        posy = self.ymid + stirrer_radius*np.sin(freq*t)
        return [posx,posy]
