# ------------------------------------------------------------------------
# packages and coding import
# ------------------------------------------------------------------------

import numpy as np
import pandas as pd

# from openpyxl import Workbook
from datetime import datetime

# import statistics
# import os
# import ntpath
# from tgcsim.models.ev import EV
# from tgcsim.models.se import SE
# from tgcsim.models.tgc import TGC
# from tgcsim.models.se_generator import SE_Generator
# from tgcsim.models.ev_generator import EV_Generator
# from ev_charge_profile import *

from salabim import App, Queue

# from plotnine import ggplot, aes, geom_point
import matplotlib.pyplot as plt

# from olp_abstract_model import *
# from energy_price import *

# ------------------------------------------------------------------------

random_seed = 4343  #'*' # 42
# np.random.seed(random_seed)
z = float("inf")  #          infinite

time_unit = "hours"  #    time unit used in the simulation
sim_time = 50
ex_plot = True

# --- Network -------------------------------------------------------------
e = z  #               number of EV's
m = 20  #                    total number of SEs
c = 20  #                    connected number of SE's
# --- OLP ----------------------------------------------------------------
n = 60  #                    time periods in the future (can become less)
# --- Enexis --------------------------------------------------------------
r = 0.5  #                     factor of Enexis grid connection
# --- Queue ---------------------------------------------------------------
q = 1  #                     lenght of queue
w = z  #                     wait time in hrs for a parking place

RLS = {
    # "EDD": "ted",  #         Earliest Due Date
    "EDF": "ted",  #         Earliest Due Date First    
    "LDD": "-ted",  #        Latest Due Date
    "FIFO": "toa",  #        First In First Out
    "LIFO": "-toa",  #       Last In First Out
    "SPT": "tid",  #         Shortest Processing Time
    "LPT": "-tid",  #        Longest Processing Time
    "SRT": "tcr",  #         Shortest Remaining Charging Time       
    "LRT": "-tcr",  #        Longest Remaining Charging Time       
    "LLX": "llx", #          Least Laxity
    "MLX": "-llx", #         Maximum Laxity
    # "RLX": "rlx", #          to be tested, dynamic - remaining laxity
}
PRIO = "SPT"
RUL = RLS[PRIO]

LAY = [True] * min(m, c) + [False] * max(m - c, 0)

iat = 10 / m  # 60 / (40 * m) # 10
dur = 8  # 60 / 50        #8

params_dict = {
    "IAT": ("exponential", iat),  #      Interarrival time 60/40
    "DUR": ("exponential", dur),  #  Duration of Stay
    "ISC": ("uniform", 0, 0),  #       State of charge% #TODO
    "DSC": ("uniform", 1, 1),  #       Desired state of charge%
    "CAP": ("uniform", 70, 70),  #       Capacity
    "DEG": ("uniform", 0.0075, 0.0075),  # Battery degradation
    "MPO": ("uniform", 7, 7),  #         EVSE max Power output
    "MPI": ("uniform", 7, 7),  #         EV max Power input
    "ENX": ("uniform", 70, 70),  #       enexis max Power output
    "CVP": ("uniform", 100, 100),  #       Start of CV phase #TODO
    "ENG": ("uniform", 0.3, 0.6),  #     Energy price
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


def enexis_plot(df, pwr, utl, sat):
    plt.step(df["t"], df[pwr], where="post", color="#DF0073")

    plt.xlabel("t")
    plt.ylabel("power [kW]")
    plt.title(
        "Enexis Utilization: "
        + str(round(100 * utl))
        + "%   "
        + "Customer Satisfaction: "
        + str(round(sat))
        + "%"
        + "\n"
        + "Enexis mpo: "
        + str(EX_MPO)
        + "kW"
        + " "
        + "Places: "
        + str(m)
        + " "
        + "Chargers: "
        + str(c)
        + "\n"
        + "prio: "
        + str(PRIO)
        + " "
        + " max. Queue length: "
        + str(q)

    )

    plt.show()



