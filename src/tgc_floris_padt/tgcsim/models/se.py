from salabim import Monitor, Component

# TODO remove next line
from tgcsim.models.ev_charge_profile import *


class SE(Component):
    """Class to model the behaviour of Supply Equipment (SE).

    Args:
        se_max_power_output (float): Maximum power output of the se. [kW]
        connected_to_grid (bool): True if connected to the grid, False if not.
    """

    def setup(
        self,
        se_max_power_output,
        connected_to_grid,
        tetris_game_charger,
        waiting_line,
        simulation_app,
    ):
        # --- Constants ---
        self._mpo = se_max_power_output
        self._con = connected_to_grid
        self._tgc = tetris_game_charger
        self._que = waiting_line
        self._app = simulation_app
        # --- Variables ---
        self._pwr = 0
        self._ppw = 0  # previous power
        # --- Objects ---
        self._evc = None  # ev being charged
        # --- Monitors ---
        self.mon_kwh = Monitor(name="SE kWh", level=True)
        self.mon_dur = Monitor(name="SE Dur", level=False)

    # --- properties Read ---
    @property
    def con(self):
        return self._con

    @property
    def mpo(self):
        return self._mpo

    @property
    def pwr(self):
        return self._pwr

    @property
    def evc(self):
        return self._evc

    @property
    def utl(self):
        return 100 * self.mon_kwh.mean(ex0=False) / self._mpo

    # --- properties Write ---
    @con.setter
    def con(self, value):
        self._con = value

    @pwr.setter
    def pwr(self, value):
        # self._ppw = self._pwr
        self._pwr = value
        self.mon_kwh.tally(self._pwr)

    # --- Methods ---
    def update_energy_charged(self):
        # self.mon_kwh.tally(self._pwr)
        self._evc.update_energy_charged(self._pwr)
        # self._evc.enr = self._ppw * slot_duration

    def get_charge_profile(self):
        if self._evc is None:
            return None
        else:
            return charge_profile(
                dur=self._evc.dur,
                csc=self._evc.s_c,
                dsc=self._evc.s_d,
                cap=self._evc.cap,
                pwr=self.pwr,
                deg=self._evc.deg,
            )

    def process(self):
        while True:
            # wait for EV to arrive
            while len(self._que) == 0:
                self.passivate()

            # assign EV
            self._evc = self._que.pop()
            self._evc.sec = self
            self._evc.toa = self._app.now()

            self._tgc.activate()
            self._tgc.remaining_duration(0, priority=0, urgent=True)

            # charge EV
            self.hold(self._evc.dur, priority=2)

            # update statistics
            self.update_energy_charged()
            self.mon_kwh.tally(0)
            self.mon_dur.tally(self._evc.dur)
            self._evc.mon_dur.tally(self._evc.dur)

            # register EV in list for Reporting
            self._evc.register(self._app.evs)

            # release EV
            self._evc = None
