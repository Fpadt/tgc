import sys
import os

# Add the grandparent directory to the system path
sys.path.append("/home/floris/tgc/src/tgc_floris_padt")

# --------------------------------------------------------------------------

from salabim import Component
from config import *


class Generator(Component):
    """Class to model the behavior of an Electrical Vehicle (ev).

    Args:

    """   
    def setup(self):
        self.rnd_dur = create_random_generator(params_dict, 'DUR')
        self.rnd_soc = create_random_generator(params_dict, 'SOC')
        self.rnd_dsc = create_random_generator(params_dict, 'DSC')        
        self.rnd_cap = create_random_generator(params_dict, 'CAP')
        self.rnd_mpi = create_random_generator(params_dict, 'MPI')        
        self.rnd_deg = create_random_generator(params_dict, 'DEG')        

    def process(self):
        while True:
            # print("Generator")
            print(f"dur {self.rnd_dur()}")
            print(f"soc {self.rnd_soc()}")
            print(f"dsc {self.rnd_dsc()}")
            print(f"cap {self.rnd_cap()}")
            print(f"mpi {self.rnd_mpi()}")
            print(f"deg {self.rnd_deg()}")
            print("")
            self.hold(10)

        # self.enter(waitingline)
        # for evse in HUB:
        #     if evse.ispassive():
        #         evse.activate()
        #         break
        # self.passivate()
        # self.register(EVS)