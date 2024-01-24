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
        self._app = simulation_app
        self._cap = ev_battery_capacity
        self._deg = battery_degradation
        self._dur = duration_of_stay
        self._fac = charging_facility
        self._mpi = ev_max_power_input
        self._mxq = max_queue_length
        # self._mxw = max_wait_time
        self._que = waiting_line
        self._rcv = ev_start_of_cv_phase_percentage / 100
        self._s_d = desired_state_of_charge
        self._s_i = initial_state_of_charge

        # --- Dynamic Read/Write ---
        self._pwr = 0
        self._sec = None
        self._ses = None
        self._toa = None
        self._tod = None

        # --- Monitors ---
        self.status.monitor(False)
        self.mode.monitor(False)
        self._mon_kwh = Monitor(name="EV_kwh", level=True, type="float")

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
    def e_v(self) -> float:
        return self._rcv * self._cap

    @property
    def ecd(self) -> float:
        return max(self.e_d - self.e_c, 0)

    @property
    def ecr(self) -> float:
        return max(self.e_r - self.e_c, 0)

    @property
    def eic(self) -> float:
        df = self._mon_kwh.as_dataframe()
        eic = df.assign(
            pt=df["t"].shift(-1),
            dt=lambda df: df["pt"] - df["t"],
            cp=lambda df: df["dt"] * df["EV_kwh.x"],
        )["cp"].sum(skipna=True)
        return eic

    @property
    def eid(self) -> float:
        return max(self.e_d - self.e_i, 0)

    @property
    def eir(self) -> float:
        return max(self.e_r - self.e_i, 0)

    @property
    def ep1(self) -> float:
        return max(self._rcv * self._cap - self.e_c, 0)

    @property
    def ep2(self) -> float:
        return max(self.e_r - self._rcv * self._cap, 0)

    @property
    def erd(self) -> float:
        return max(self.e_d - self.e_r, 0)

    @property
    def llx(self) -> float:
        return np.NaN if self._sec is None else self.ted - self.tcr

    @property
    def mon_kwh(self):
        return self._mon_kwh

    @property
    def mpi(self) -> float:
        return self._mpi

    @property
    def p_d(self) -> float:
        return self.pp1 if self.tp1 > 0 else self.pp2

    @property
    def pp1(self) -> float:
        return 0 if self.tp1 == 0 else self.ep1 / self.tp1

    @property
    def pp2(self) -> float:
        return 0 if self.tp2 == 0 else self.ep2 / self.tp2

    @property
    def pwr(self) -> float:
        #  mpi if e_r-e_c<0
        return self._pwr

    @property
    def s_c(self) -> float:
        return 0 if self._cap == 0 else self.e_c / self._cap

    @property
    def s_d(self) -> float:
        return self._s_d

    @property
    def s_i(self) -> float:
        return self._s_i

    @property
    def s_r(self) -> float:
        return 0 if self._cap == 0 else self.e_r / self._cap

    @property
    def sat(self) -> float:
        return 100 if self.eir ==0 else 100 * self.eic / self.eir

    @property
    def scd(self) -> float:
        return 0 if self._cap == 0 else self.ecd / self._cap

    @property
    def scr(self) -> float:
        return 0 if self._cap == 0 else self.ecr / self._cap

    @property
    def sec(self) -> float:
        return self._sec

    @property
    def ses(self) -> float:
        return self._ses

    @property
    def sic(self) -> float:
        return 0 if self._cap == 0 else self.eic / self._cap

    @property
    def sid(self) -> float:
        return 0 if self._cap == 0 else self.eid / self._cap

    @property
    def sir(self) -> float:
        return 0 if self._cap == 0 else self.eir / self._cap

    @property
    def srd(self) -> float:
        return 0 if self._cap == 0 else self.erd / self._cap

    @property
    def t_d(self) -> float:
        return self.tp1 if self.tp1 > 0 else self.tp2

    @property
    def tcd(self) -> float:
        return 0 if self.mpi == 0 else self.ecd / self._mpi  # TODO

    @property
    def tcr(self) -> float:
        return 0 if self.mpi == 0 else self.ecr / self._mpi  # TODO

    @property
    def tic(self) -> float:
        return 0 if self.mpi == 0 else self.eic / self.mpi  # TODO

    @property
    def tid(self) -> float:
        return 0 if self.mpi == 0 else self.eid / self._mpi  # TODO

    @property
    def tir(self) -> float:
        return 0 if self.mpi == 0 else self.eir / self._mpi  # TODO

    @property
    def toa(self) -> float:
        return self._toa
    
    @property
    def ted(self) -> float:
        return float("inf") if self._sec is None else self._toa + self._dur

    @property
    def tod(self) -> float:
        return self._tod

    @property
    def tp1(self) -> float:
        return 0 if self.mpi == 0 else self.ep1 / self.mpi  # TODO

    @property
    def tp2(self) -> float:
        # Solve the equation numerically
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html

        sol = 0
        if self.ep2 > 0:
            sol = fsolve(
                func=zero_for_E,
                x0=0,
                args=(0, self.mpi, self._deg, self.ep2),  # TODO
                xtol=1e-2,
            )[0]

        return sol

    @property
    def trd(self) -> float:
        return 0 if self._pwr == 0 else self.erd / self._mpi  # TODO

    # --- properties Write ---

    @pwr.setter
    def pwr(self, value):
        self._pwr = value
        if self.sec is not None:
            self._mon_kwh.tally(self._pwr)
            self._sec.mon_kwh.tally(self._pwr)
        if self._pwr == 0:
            self.passivate()
        else:
            self.activate()

    @sec.setter
    def sec(self, se):
        self._sec = se
        if se is not None:
            self._ses = self._sec.name() + "/" + self.name()

    @toa.setter
    def toa(self, value):
        self._toa = value
        self._mon_kwh.reset(True)

    @tod.setter
    def tod(self, value):
        self._tod = value

    # --- Methods --- 
    def process(self):
        # check if queue is full
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
        self.passivate()

        # # if not serviced within this time, renege
        # self.hold(self._mxw, priority=1)
        # if self in self._que:
        #     self.leave(self._que)
        #     self._app.number_reneged += 1
        # else:
        # start charging

        # Phase 1: charge till ev_start_of_cv_phase_percentage (80%)
        while self._sec is not None and self.e_c <= self.e_v:
            self._sec.request_power()
            self.hold(self.t_d, priority=1)
            self.pwr = 0

        # Phase 2: charge till realistic energy level is reached
        while self._sec is not None and self.e_v < self.e_c <= self.e_r:
            self._sec.request_power()
            self.hold(self.t_d, priority=1)
            self.pwr = 0

        # prepare to leave
        self._sec.request_power()
        self.pwr = 0