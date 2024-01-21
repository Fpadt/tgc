from tgcsim.models.ev import EV
from tgcsim.models.se import SE
from tgcsim.models.tgc import TGC
from tgcsim.models.se_generator import SE_Generator
from tgcsim.models.ev_generator import EV_Generator

from salabim import App, Queue


class TGC_network:
    def __init__(
        self,
        enexis_max_power_output,
        priority_rule,
        simulation_app,
        distributions_dict,
        layout,
        number_of_evs,
        max_queue_length,
        max_wait_time,
    ):
        self._mpo = enexis_max_power_output
        self._rul = priority_rule
        self._app = simulation_app
        self._dis = distributions_dict
        self._lay = layout
        self._nev = number_of_evs
        self._mxq = max_queue_length
        self._mxw = max_wait_time

    @property
    def que(self):
        return self._que

    @property
    def tgc(self):
        return self._tgc
    
    @property
    def fac(self):
        return self._fac
    
    @property
    def flt(self):
        return self._flt
    

    def create_network(self):
        # instantiate the waiting line
        self._que = Queue(
            name="Facility waitingline",
        )
        self._que.length_of_stay.reset_monitors(stats_only=True)

        # instantiate Tetris Game Charger
        self._tgc = TGC(
            name="Tetris Game Charger",
            enexis_max_power_output=self._mpo,
            priority_rule=self._rul,
            simulation_app=self._app,
        )

        # instantiate the facility with Supply Equipment (chargers)
        self._fac = SE_Generator(
            distributions_dict=self._dis,
            layout=self._lay,
            simulation_app=self._app,
        )

        # instantiate the EV generator (EV-Fleet)
        self._flt = EV_Generator(
            distributions_dict=self._dis,
            number_of_evs=self._nev,
            max_queue_length=self._mxq,
            max_wait_time=self._mxw,
            simulation_app=self._app,
        )

        # connect the network
        self._tgc.fac = self._fac
        self._fac.tgc = self._tgc
        self._fac.que = self._que
        self._flt.fac = self._fac
        self._flt.que = self._que
