import numpy as np
import pandas as pd
from openpyxl import Workbook
from datetime import datetime
import statistics
import os
import ntpath

np.random.seed(42)

m = 20  #                   number of EVSEs
n = 60  #                   time periods in the future (can become less)
r = 0.5  #                  factor of Enexis grid connection

# --------------------------------------------------------------------------
# The array's for all EV's & SE together and the resulting minimum.
# EV = np.random.choice([EV_MPI, EV_MPI / 2, 3.33, 3.33 / 2], size=(m, n))
# SE = np.random.choice([SE_MPO], size=(m, n))
# EVSE = np.minimum(EV, SE)


params_dict = {
    "SOC": ("uniform", 0, 0.2), #       State of charge
    "DSC": ("uniform", 0.4, 1), #       Desired state of charge
    "DUR": ("uniform", 1, 8), #         Duration of Stay
    "ENG": ("uniform", 0.3, 0.6), #     Energy price
    "CAP": ("uniform", 70, 70), #       Capacity
    "DEG": ("uniform", 0.075, 0.075), # Battery degradation
    "MPO": ("uniform", 7, 7), #         EVSE max Power output 
    "MPI": ("uniform", 7, 7), #         EV max Power input
    }

# SE_MPO = 7  #               EVSE max Power output for each time period
# EV_MPI = 7  #               EV max Power input for each time period
# EX_MPO = m * r * SE_MPO  #  enexis max Power output for each time period (constant)
# CAP = cap_l  #                 EV max capacity of battery
# K = 0.075  #                EV battery degradation cost per kWh

# --------------------------------------------------------------------------

# soc_l = 0.0  #              lower bound of state of charge
# soc_h = 0.2  #              upper bound of state of charge
# d_c_l = 0.4  #              lower bound of desired charge
# d_c_h = 1.0  #              upper bound of desired charge
# dur_l = 1.0  #              lower bound of parking duration
# dur_h = 8.0  #              upper bound of parking duration
# eng_l = 0.3  #              lower bound of energy price
# eng_h = 0.6  #              upper bound of energy price

# cap_l = 70.0  #             lower bound of battery capacity
# cap_h = 70.0  #             upper bound of battery capacity
# k_l = 0.075  #              lower bound of battery degradation
# k_h = 0.075  #              upper bound of battery degradation

# mpo_l = 3.0  #              lower bound of EVSE max power output
# mpo_h = 7.0  #              upper bound of EVSE max power output
# mpi_l = 3.0  #              lower bound of EV   max power input
# mpi_h = 7.0  #              upper bound of EV   max power input

p_rnd = True  #             will energyprice be random of linear

# --------------------------------------------------------------------------
# olp specific
# --------------------------------------------------------------------------

alpha = 1.0  #              EVSE efficiency
beta = 1.0  #               customer satisfaction
gamma = 1.0  #              cost of energy

# --------------------------------------------------------------------------
print_solver_outcome = False
print_EVSE_power = False

print_session_max_charge = False
print_remaining_charge = False

print_parking_time = False
print_energy_price = False

print_tee = False

# Set the solver to be used
# solver = "ipopt" #        m 50 EVSE's, > 50 time periods
# solver = "mosek" #        m 50 EVSE's, > 50 time periods
# solver = "cplex"  #       m 50 EVSE's, 18 time periods
solver = "glpk"  #          m 50 EVSE's, > 50 time periods
# solver = "gurobi" #       m xx EVSE's, 19 time periods - no license yet

# --------------------------------------------------------------------------

def create_random_generator(params_dict, key):
    params = params_dict.get(key)
    if params is None:
        raise ValueError(f"No parameters found for key: {key}")

    distribution = params[0]
    params = params[1:]

    if distribution == 'uniform':
        low, high = params
        return lambda: np.random.uniform(low, high)
    elif distribution == 'normal':
        mu, sigma = params
        return lambda: np.random.normal(mu, sigma)
    elif distribution == 'poisson':
        lam = params[0]
        return lambda: np.random.poisson(lam)
    elif distribution == 'gamma':
        shape, scale = params
        return lambda: np.random.gamma(shape, scale)
    else:
        raise ValueError(f"Unknown distribution: {distribution}")


