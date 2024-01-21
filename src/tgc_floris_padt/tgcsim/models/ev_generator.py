from salabim import Component

from tgcsim.models.ev import EV
from tgcsim.models.distr_func_factory import create_random_generator

# --------------------------------------------------------------------------
# Generator which creates EV's up to a certain number
class EV_Generator(Component):
    """Class to model the behaviour of an Electrical Vehicle (ev).

    Args:
        number_of_evs (int): Number of EVs to be generated.
    """

    def setup(
        self,
        distributions_dict,
        number_of_evs,
        charging_facility,
        waiting_line,
        max_queue_length,
        max_wait_time,
        simulation_app,
    ):
        self._dis = distributions_dict
        self._nev = number_of_evs        
        self._fac = charging_facility
        self._que = waiting_line
        self._mxq = max_queue_length
        self._mxw = max_wait_time
        self._app = simulation_app
        self._iat = create_random_generator(self._dis, "IAT")
        self._dur = create_random_generator(self._dis, "DUR")
        self._isc = create_random_generator(self._dis, "ISC")
        self._dsc = create_random_generator(self._dis, "DSC")
        self._cap = create_random_generator(self._dis, "CAP")
        self._mpi = create_random_generator(self._dis, "MPI")
        self._deg = create_random_generator(self._dis, "DEG")

    def process(self):
        i = 1
        while i <= self._nev:
            # take a sample from the distributions and relate
            dur = self._dur()
            cap = self._cap()
            mpi = self._mpi()
            isc = self._isc()
            dsc = self._dsc()  # 1 * dur * mpi / cap + isc #
            # create EV and assign random values
            ev = EV(
                duration_of_stay=dur,
                initial_state_of_charge=isc,
                desired_state_of_charge=dsc,
                ev_battery_capacity=cap,
                ev_max_power_input=mpi,
                battery_degradation=self._deg(),
                charging_facility=self._fac,
                waiting_line=self._que,
                max_queue_length=self._mxq,
                max_wait_time=self._mxw,
                simulation_app=self._app,
            )

            # hold for interarrival time
            self.hold(self._iat(), priority=1)
            i += 1


