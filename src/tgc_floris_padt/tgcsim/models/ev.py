from salabim import Monitor, Component
# from config import *

class EV(Component):
    """Class to model the behavior of an Electrical Vehicle (ev).

    Args:
        arrival (int): Arrival time of the ev. [periods]
        estimated_departure (int): Estimated departure time of the ev. [periods]
        state_of_charge (float): State of charge of the ev on arrival. [kWh]
        desired_state_of_charge (float): Desired state of charge of the ev on departure. [kWh]
        ev_battery_capacity (float): Capacity of the ev battery. [kWh]
        ev_max_power_input (float): Maximum power input of the ev. [kW]
        battery_degradation (float): Battery degradation factor of the ev. [kW]
        station_id (str): Identifier of the EVSE station used by this ev.
        session_id (str): Identifier of the session belonging to this ev.
    """

    def setup(
        self,
        arrival,
        estimated_departure,
        state_of_charge,
        desired_state_of_charge,
        ev_battery_capacity,
        ev_max_power_input,
        battery_degradation,
        station_id,
        session_id,
    ):
        self.stay = estimated_departure - arrival  
        self.soc = state_of_charge  
        self.d_c = desired_state_of_charge
        self.cap = ev_battery_capacity
        self.mpi = ev_max_power_input
        self.k = battery_degradation  
        # ----------------------------------
        self.toa = arrival
        self.tod = estimated_departure
        self.tcb = None  # time of charge begin
        self.dc = desired_state_of_charge * ev_battery_capacity 
        self.ckwh = 0  # final charge in kWh
        # ----------------------------------
        self.m_stay = Monitor(name="stay", level=False)
        self.m_kwh = Monitor(name="kwh", level=False)

