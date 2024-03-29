from salabim import Monitor, Component

import numpy as np

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
        self._toa = None
        self._ses = None
        # --- Objects ---
        self._evc = None  # ev being charged
        # --- Monitors ---
        self.status.monitor(False)
        self.mode.monitor(False)
        self._mon_kwh = Monitor(name="SE_kWh", level=True, type='float')
        self._mon_dur = Monitor(name="SE_dur", level=False, type='float')

    # --- properties Read ---
    @property
    def con(self):
        return self._con

    @property
    def evc(self):
        return self._evc

    @property
    def mpo(self):
        return self._mpo

    @property
    def mon_kwh(self):
        return self._mon_kwh    

    @property
    def pwr(self):
        return self._pwr
    
    @property
    def ses(self) -> float:
        return self._ses

    @property
    def toa(self):
        return self._toa

    @property
    def tod(self):
        return float("inf") if self._evc is None else self._toa + self._evc.dur

    @property
    def utl(self):
        return 100 * self._mon_kwh.mean(ex0=False) / self._mpo

    @evc.setter
    def evc(self, ev):
        self._evc = ev
        if ev is not None:
            self._ses = self.name() + "/" + self._evc.name()        


    @pwr.setter
    def pwr(self, value):
        self._pwr = min(value, self._mpo)
        if self._evc is not None:
            self._evc.pwr = self._pwr

    @toa.setter
    def toa(self, value):
        self._toa = value
        self._evc.toa = value

    # --- Methods ---
    def request_power(self) -> None:
        """Request power from the SE."""
        self._tgc.request_power()
        return None

    def process(self):
        while True:
            # wait for EV to arrive
            while len(self._que) == 0:
                self.passivate()

            # Connect SE/EV
            self.evc = self._que.pop()
            self._evc.sec = self

            # registrate start time of charge
            self.toa = self._app.now()
            self._evc.activate()

            # Park EV (EV determines if charging)
            self.hold(self._evc.dur, priority=2)

            # EV leaving, disconnect and deactivate loading & monitoring
            self._evc.pwr = 0
            self._evc.tod = self._app.now()

            self._mon_dur.tally(self._evc.dur)

            # register EV in list for Reporting
            self._evc.register(self._app.evs)

            # release EV
            self._evc.sec = None
            self._evc = None
            self._mon_kwh.tally(0)