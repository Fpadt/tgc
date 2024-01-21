from salabim import Monitor, Component
from scipy.optimize import fsolve
import numpy as np

def cv_pwr(t: float, pm: float, k: float) -> float:
    """
    Calculate the charging power for a given time.

    Parameters
    ----------
    t : float
        Time in hours.
    pm : float
        Maximum power input of the EV in kW.
    k : float
        Charging curve constant.
        0.01-0.03 charge aggressively,
        0.05-0.1  prioritizing battery health and longevity
    """
    return pm * np.exp(-k * t)


def cv_eng(t2, t1, pm, k) -> float:
    """
    Calculate the charging energy for a given time interval (t2, t1)
    note: t2 > t1

    Parameters
    ----------
    t2 : float
        End time in hours.
    t1 : float
        Start time in hours.
    pm : float
        Maximum power input of the EV in kW.
    k : float
        Charging curve constant.
        0.01-0.03 charge aggressively,
        0.05-0.1  prioritizing battery health and longevity
    """
    return (-1 / k) * (cv_pwr(t2, pm, k) - cv_pwr(t1, pm, k)) 

# Define the function for the given equation with specific ta, pm and k
def zero_for_E(t2, t1, pm, k, E) -> float:
    """
    function to solve the root of the equation, so where it is 0

    Parameters
    ----------
    t2 : float
        End time in hours.
    t1 : float
        Start time in hours.
    pm : float
        Maximum power input of the EV in kW.
    k : float
        Charging curve constant.
        0.01-0.03 charge aggressively,
        0.05-0.1  prioritizing battery health and longevity
    E : float
        Energy in kWh to be charged
    """
    return cv_eng(t2, t1, pm, k) - E


class EV(Component):
    """Class to model the behavior of an Electrical Vehicle (ev).

    Args:
        duration_of_stay (float): Duration of the ev stay. [h]
        initial_state_of_charge (float): State of charge of the ev on arrival. [kWh]
        desired_state_of_charge (float): Desired state of charge of the ev on departure. [kWh]
        ev_battery_capacity (float): Maximum Capacity of the ev battery. [kWh]
        ev_max_power_input (float): Maximum power input of the ev. [kW]
        battery_degradation (float): Battery degradation factor of the ev. [kW]
    """

    def setup(
        self,
        duration_of_stay,
        initial_state_of_charge,
        desired_state_of_charge,
        ev_battery_capacity,
        ev_start_of_cv_phase_percentage,
        ev_max_power_input,
        battery_degradation,
        charging_facility,
        waiting_line,
        max_queue_length,
        max_wait_time,
        simulation_app,
    ):
        # --- set by setup parameters ---
        self._cap = ev_battery_capacity
        self._cvp = ev_start_of_cv_phase_percentage / 100
        self._deg = battery_degradation
        self._dur = duration_of_stay
        self._mpi = ev_max_power_input
        self._s_d = desired_state_of_charge
        self._s_i = initial_state_of_charge
        self._fac = charging_facility
        self._que = waiting_line
        self._mxq = max_queue_length
        self._mxw = max_wait_time
        self._app = simulation_app
        # --- Dynamic Read/Write ---
        self._pwr = 7  # TODO
        self._sec = None
        self._toa = None
        self._tss = None  # TODO still needed?

        # --- Monitors ---
        self.mon_kwh = Monitor(name="EV kWh", level=True)  # TODO remove
        self.mon_dur = Monitor(name="EV Dur", level=False)  # TODO remove
        self.mon_pwr = Monitor(name="EV_pwr", level=True)

    # --- Properties Read ---
    @property
    def cap(self) -> float:
        return self._cap

    @property
    def deg(self) -> float:
        return self._deg

    @property
    def dur(self) -> float:
        return self._dur

    @property
    def e_c(self) -> float:
        return self.e_i + self.eic

    @property
    def e_d(self) -> float:
        return self._s_d * self._cap

    @property
    def e_i(self) -> float:
        return self._s_i * self._cap

    @property
    def e_r(self) -> float:
        return min(self.e_i + self._dur * self._mpi, self.e_d)

    @property
    def ecd(self) -> float:
        return self.e_d - self.e_c

    @property
    def ecr(self) -> float:
        return self.e_r - self.e_c

    @property
    def eic(self) -> float:
        df = self.mon_pwr.as_dataframe()
        eic = df.assign(
            pt=df["t"].shift(-1),
            dt=lambda df: df["pt"] - df["t"],
            cp=lambda df: df["dt"] * df["EV_pwr.x"],
        )["cp"].sum(skipna=True)
        return eic

    @property
    def eid(self) -> float:
        return self.e_d - self.e_i

    @property
    def eir(self) -> float:
        return self.e_r - self.e_i

    @property
    def ep1(self) -> float:
        return max(self._cvp * self._cap - self.e_c, 0)

    @property
    def ep2(self) -> float:
        return max(self.e_r - self._cvp * self._cap, 0)

    @property
    def ep3(self) -> float:
        return 0

    @property
    def erd(self) -> float:
        return self.e_d - self.e_r

    @property
    def llx(self) -> float:
        return self.tod - self.tcr

    @property
    def mpi(self) -> float:
        return self._mpi

    @property
    def pwr(self) -> float:
        #  mpi if e_r-e_c<0
        return self._pwr

    @property
    def p_r(self) -> float:
        return min(self._mpi, self._sec.mpo)
    
    @property
    def s_c(self) -> float:
        return self.e_c / self._cap

    @property
    def s_d(self) -> float:
        return self._s_d

    @property
    def s_i(self) -> float:
        return self._s_i

    @property
    def s_r(self) -> float:
        return self.e_r / self._cap

    @property
    def sat(self) -> float:
        return self.eic / self.eir

    @property
    def scd(self) -> float:
        return self.ecd / self._cap

    @property
    def scr(self) -> float:
        return self.ecr / self._cap

    @property
    def sec(self) -> float:
        return self._sec
    
    @property
    def ses(self) -> float:
        return self._sec.name() + "/" + self.name()

    @property
    def sic(self) -> float:
        return self.eic / self._cap

    @property
    def sid(self) -> float:
        return self.eid / self._cap

    @property
    def sir(self) -> float:
        return self.eir / self._cap

    @property
    def srd(self) -> float:
        return self.erd / self._cap

    @property
    def tcd(self) -> float:
        return self.ecd / self._pwr

    @property
    def tcr(self) -> float:
        return self.ecr / self._pwr

    @property
    def tic(self) -> float:
        return self.eic / self.pwr

    @property
    def tid(self) -> float:
        return self.eid / self._pwr

    @property
    def tir(self) -> float:
        return self.eir / self._pwr

    @property
    def toa(self) -> float:
        return self._toa

    @property
    def tod(self) -> float:
        return self._toa + self._dur

    @property
    def tp1(self) -> float:
        return min(self.ep1 / self._mpi, self.tp3)

    @property
    def tp2(self) -> float:
        # Solve the equation numerically
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html
        
        # TODO: replace self._mpi by self.p_r on all places
        sol = 0
        if self.ep2 > 0:
            sol = fsolve(func=zero_for_E, x0=0, args=(0, self._mpi, self._deg, self.ep2), xtol=1e-2)[0]

        return sol

    @property
    def tp3(self) -> float:
        return max(self.tod - self._app.now(), 0)

    @property
    def trd(self) -> float:
        return self.erd / self._pwr

    @property  # TODO still needed?
    def tss(self) -> float:
        return self._tss

    # --- properties Write ---

    # @pwr.setter
    # def pwr(self, value):
    #     energy_charged = (self._app.now() - self._tss) * self._ppw
    #     self.cle += energy_charged
    #     # self.mon_kwh.tally(energy_charged)
    #     self._ppw = self._pwr
    #     self._tss = self._app.now()
    #     self._pwr = value

    @sec.setter
    def sec(self, se):
        self._sec = se

    @toa.setter
    def toa(self, start_time_of_charge):
        self._toa = start_time_of_charge
        self._tss = self._toa

    # --- Methods --- TODO replace by power to mon
    def update_energy_charged(self, power):
        energy_charged = (self._app.now() - self._tss) * power
        # self.cle += energy_charged
        self.mon_kwh.tally(energy_charged)
        self._tss = self._app.now()

    def process(self):
        if len(self._que) >= self._mxq:
            self._app.number_balked += 1
            self.cancel()
        # enter the waiting line
        self.enter(self._que)
        # check if any SE is available
        for se in self._fac.fac:
            if se.ispassive():
                se.activate()
                break
        self.hold(self._mxw, priority=1)  # if not serviced within this time, renege
        if self in self._que:
            self.leave(self._que)
            self._app.number_reneged += 1
        else:
            self.passivate()  # wait for service to be completed
