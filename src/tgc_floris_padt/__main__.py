# ------------------------------------------------------------------------
# packages and coding import
# ------------------------------------------------------------------------

# packages
import salabim as sim
from tgcsim.models.generator import Generator

# from config import *
# from ev_charge_profile import *
# from olp_abstract_model import *
# from energy_price import *

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

app = sim.App(
    trace=False,  # defines whether to trace or not
    # random_seed=random_seed,  # if “*”, a purely random value (based on the current time)
    # time_unit=time_unit,  # defines the time unit used in the simulation
    # name="Charging Station",  # name of the simulation
    # do_reset=True,  # defines whether to reset the simulation when the run method is called
    yieldless=True,  # defines whether the simulation is yieldless or not
)

# Instantiate and activate the EV generator
Generator()

    # # Create Queue and set monitor to stats_only
    # # https://www.salabim.org/manual/Queue.html
    # waitingline = sim.Queue(name="Waiting Cars", monitor=True)
    # # waitingline.length_of_stay.monitor(value=True)
    # waitingline.length.reset_monitors(stats_only=True)
    # waitingline.length_of_stay.reset_monitors(stats_only=True)

    # # Instantiate the servers, list comprehension but only 1 server
    # ChargingStations = [ChargingStation() for _ in range(N_STATION)]

    # Execute Simulation
app.run(till=100)

# --------------------------------------------------------------------------
# Reporting Results
# --------------------------------------------------------------------------