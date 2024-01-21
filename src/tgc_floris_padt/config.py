# ------------------------------------------------------------------------
# packages and coding import
# ------------------------------------------------------------------------

# import salabim as sim
import numpy as np
import pandas as pd
# from openpyxl import Workbook
from datetime import datetime
# import statistics
# import os
# import ntpath
from tgcsim.models.ev import EV
from tgcsim.models.se import SE
from tgcsim.models.tgc import TGC
from tgcsim.models.se_generator import SE_Generator
from tgcsim.models.ev_generator import EV_Generator
from ev_charge_profile import *

from salabim import App, Queue

from plotnine import ggplot, aes, geom_point
import matplotlib.pyplot as plt
# from olp_abstract_model import *
# from energy_price import *

# ------------------------------------------------------------------------

random_seed = 4343  #'*' # 42
# np.random.seed(random_seed)
z = float("inf")  #          infinite

time_unit = "hours"  #    time unit used in the simulation
sim_time = 500
# tgc_hold = 1  #            time to hold the tgc

# --- Network -------------------------------------------------------------
e = z  #                     number of EV's
m = 20  #                    total number of SEs
c = 10  #                    connected number of SE's
# --- OLP ----------------------------------------------------------------
n = 60  #                    time periods in the future (can become less)
# --- Enexis --------------------------------------------------------------
r = 1  #                     factor of Enexis grid connection
# --- Queue ---------------------------------------------------------------
q = z  #                     lenght of queue
w = z  #                     wait time in hrs for a parking place

RUL = "FIFO"

LAY = [True] * min(m, c) + [False] * max(m - c, 0)

iat = 10 #60 / (40 * m) # 10
dur = 8 # 60 / 50        #8

params_dict = {
    "IAT": ("exponential", iat),  #      Interarrival time 60/40
    "DUR": ("exponential", dur),  #  Duration of Stay 
    "ISC": ("uniform", 0, 0.5),  #       State of charge%
    "DSC": ("uniform", 0.5, 1),  #       Desired state of charge%
    "ENG": ("uniform", 0.3, 0.6),  #     Energy price
    "CAP": ("uniform", 70, 70),  #       Capacity
    "DEG": ("uniform", 0.00, 0.0),  # Battery degradation TODO
    "MPO": ("uniform", 7, 7),  #         EVSE max Power output
    "MPI": ("uniform", 7, 7),  #         EV max Power input
    "ENX": ("uniform", 70, 70),  #       enexis max Power output
}

EX_MPO = (
    c * r * params_dict["MPO"][1]
)  #  enexis max Power output for each time period (constant)

# --------------------------------------------------------------------------

print_ev_details = True
print_se_details = True

print_solver_outcome = False
print_EVSE_power = False

print_session_max_charge = False
print_remaining_charge = False

print_parking_time = False
print_energy_price = False

print_tee = False

# --------------------------------------------------------------------------
# olp specific
# --------------------------------------------------------------------------

alpha = 1.0  #              EVSE efficiency
beta = 1.0  #               customer satisfaction
gamma = 1.0  #              cost of energy

# --------------------------------------------------------------------------

# Set the solver to be used
# solver = "ipopt" #        m 50 EVSE's, > 50 time periods
# solver = "mosek" #        m 50 EVSE's, > 50 time periods
# solver = "cplex"  #       m 50 EVSE's, 18 time periods
solver = "glpk"  #          m 50 EVSE's, > 50 time periods
# solver = "gurobi" #       m xx EVSE's, 19 time periods - no license yet

# --------------------------------------------------------------------------


