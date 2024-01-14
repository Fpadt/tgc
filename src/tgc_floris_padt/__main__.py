# ------------------------------------------------------------------------
# packages and coding import
# ------------------------------------------------------------------------

# packages
import salabim as sim
from config import *
from ev_charge_profile import *

# from tgcsim.models.generator import EV_Generator, SE_Generator

# from olp_abstract_model import *
# from energy_price import *

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------


class EV(sim.Component):
    """Class to model the behavior of an Electrical Vehicle (ev).

    Args:
        duration_of_stay (float): Duration of the ev stay. [h]
        state_of_charge (float): State of charge of the ev on arrival. [kWh]
        desired_state_of_charge (float): Desired state of charge of the ev on departure. [kWh]
        ev_battery_capacity (float): Capacity of the ev battery. [kWh]
        ev_max_power_input (float): Maximum power input of the ev. [kW]
        battery_degradation (float): Battery degradation factor of the ev. [kW]
    """

    def setup(
        self,
        duration_of_stay,
        state_of_charge,
        desired_state_of_charge,
        ev_battery_capacity,
        ev_max_power_input,
        battery_degradation,
    ):
        # --- Constants ---
        self.dur = duration_of_stay
        self.soc = state_of_charge
        self.dsc = desired_state_of_charge
        self.cap = ev_battery_capacity
        self.mpi = ev_max_power_input
        self.deg = battery_degradation

        # --- Variables ---
        self.toa = None  #                   self.app.now()
        self.tod = None
        self.dec = desired_state_of_charge * ev_battery_capacity
        self.t2c = self.dec / self.mpi  #    estimated time to charge
        self.llx = None  #                   least Laxity
        self.ses = None
        # --- Monitors ---
        self.mon_kwh = sim.Monitor(name="EV kWh", level=True)
        self.mon_dur = sim.Monitor(name="EV Dur", level=False)

    @property
    def state_of_charge(self):
        return self.mon_kwh.duration(ex0=True) * self.mon_kwh.mean(ex0=True)

    def process(self):
        if len(QUE) >= q:
            app.number_balked += 1
            # app.print_trace("", "", "balked")
            # print(app.now(), "balked", self.name())
            self.cancel()
        # enter the waiting line
        self.enter(QUE)
        # check if any SE is available
        for se in HUB.ses:
            if se.ispassive():
                se.activate()
                break
        self.hold(w)  # if not serviced within this time, renege
        if self in QUE:
            self.leave(QUE)
            app.number_reneged += 1
            # app.print_trace(app.now(), "reneged", self.name())
        else:
            self.passivate()  # wait for service to be completed
        # statistics
        self.mon_kwh.tally(0)
        # register EV in list for Reporting
        # self.register(EVS)


class SE(sim.Component):
    """Class to model the behaviour of Supply Equipment (SE).

    Args:
        se_max_power_output (float): Maximum power output of the se. [kW]
        connected_to_grid (bool): True if connected to the grid, False if not.
    """

    def setup(self, se_max_power_output, connected_to_grid):
        # --- Constants ---
        self.mpo = se_max_power_output
        self.con = connected_to_grid
        # --- Variables ---
        self.pwr = 0
        # --- Objects ---
        self.ev = None
        # --- Monitors ---
        self.mon_kwh = sim.Monitor(name="SE kWh", level=True)
        self.mon_dur = sim.Monitor(name="SE Dur", level=False)

    @property
    def utilization(self):
        return 100 * self.mon_kwh.mean(ex0=False) / self.mpo

    def update_energy_charged(self):
        self.mon_kwh.tally(self.pwr)
        self.ev.mon_kwh.tally(self.pwr)

    def get_charge_profile(self):
        if self.ev is None:
            return None
        else:
            return charge_profile(
            dur=self.ev.dur,
            soc=self.ev.soc,
            dsc=self.ev.dsc,
            cap=self.ev.cap,
            ev_mpi=self.ev.mpi,
            se_mpo=self.mpo,
            k=self.ev.deg,
    )

    def process(self):
        while True:
            # wait for EV to arrive
            while len(QUE) == 0:
                self.passivate()
            # assign EV
            self.ev = QUE.pop()
            self.ev.ses = self.name() + "-" + self.ev.name()
            self.ev.toa = app.now()
            self.ev.tod = self.ev.toa + self.ev.dur
            self.ev.llx = self.ev.tod - self.ev.t2c
            # charge EV
            self.hold(self.ev.dur)

            # update statistics
            self.update_energy_charged()
            self.mon_kwh.tally(0)
            self.mon_dur.tally(self.ev.dur)
            self.ev.mon_dur.tally(self.ev.dur)
            # release EV
            self.ev.activate()
            self.ev = None


class TGC(sim.Component):
    def setup(self):
        # --- Objects ---
        self.schedule = app.Queue("SCHEDULE")

    def make_schedule(self, property_name):
        """Make a schedule of EVSEs sorted on property_name"""
        # new schedule
        self.schedule.clear()

        # If property_name starts with a minus sign, reverse the order
        reverse = 1
        if property_name[0] == "-":
            reverse = -1
            property_name = property_name[1:]

        # Create schedule sorted on property_name
        # add the EVSE without EV at then end to make it complete
        for se in HUB.ses:
            if se.ev is None or se.con == False:
                property_value = float("inf")
            else:
                property_value = reverse * getattr(se.ev, property_name)
            self.schedule.add_sorted(se, property_value)

        return self.schedule

    def print_state(self, se):
        if se.ev is None:
            None
            # print(f"{app.now()}\t - NO_EV/{se.name()} ")
        else:
            #   toa: {se.ev.toa} - tod: {se.ev.tod} -  \
            print(
                f"""{app.now()}\t{se.ev.name()}/{se.name()}\tcsc: {se.ev.state_of_charge}"""
                # \tpwr: {se.pwr}\tdsc: {round(se.ev.dsc)}  rem: {se.remaining_duration()}\tsch: {se.scheduled_time()}"""
            )

    def print_charge(self, se):
        if se.ev is None:
            print(f"{app.now()}\t - NO_EV/{se.name()} ")
        else:
            print(
                se.get_charge_profile()
                # f"{env.now()}\t - {evse.ev.name()}/{evse.name()} - pwr: {evse.pwr}\
                #   dc: {round(evse.ev.dc)} - ckwh: {round(evse.ev.ckwh)} - \
                #   rem: {evse.remaining_duration()} sch: {evse.scheduled_time()}"
            )    

    def assign_power(self):
        """Assign power to EVSEs according to priority
        Start with the total Power available fro Enexis
        assign according to priority set by sorting on property
        """
        # initialize the available power to the total power available
        available_power = EX_MPO
        # make a schedule
        order = self.make_schedule(RLS[RUL])
        # order.print_info()
        # assign power to EVSEs
        while len(order) > 0:
            se = order.pop()
            if se.ev == None:
                se.pwr = 0
            else:
                se.pwr = se.con * min(
                    [
                        se.mpo,
                        available_power,
                        se.ev.mpi,
                    ]
                )

            available_power -= se.pwr
            available_power = max(available_power, 0)  # note may not be negative
            # print(f"available_power: {available_power}")

    def update_se_enerygy_charged(self):
        for se in HUB.ses:
            if se.ev is not None:
                se.update_energy_charged()

    def process(self):
        while True:
            self.assign_power()  # TODO
            self.update_se_enerygy_charged()
            # statistics
            # [self.print_state(x) for x in HUB.ses]
            [self.print_charge(x) for x in HUB.ses]    

            self.standby()  # makes it run every event


# --------------------------------------------------------------------------
# Generators
class EV_Generator(sim.Component):
    """Class to model the behaviour of an Electrical Vehicle (ev).

    Args:
        number_of_evs (int): Number of EVs to be generated.
    """

    def setup(self, number_of_evs):
        self.cnt_evs = number_of_evs
        self.rnd_iat = create_random_generator(params_dict, "IAT")
        self.rnd_dur = create_random_generator(params_dict, "DUR")
        self.rnd_soc = create_random_generator(params_dict, "SOC")
        self.rnd_dsc = create_random_generator(params_dict, "DSC")
        self.rnd_cap = create_random_generator(params_dict, "CAP")
        self.rnd_mpi = create_random_generator(params_dict, "MPI")
        self.rnd_deg = create_random_generator(params_dict, "DEG")

        self.evs = []

    def process(self):
        i = 1
        while i <= self.cnt_evs:
            ev = EV(
                duration_of_stay=self.rnd_dur(),
                state_of_charge=self.rnd_soc(),
                desired_state_of_charge=self.rnd_dsc(),
                ev_battery_capacity=self.rnd_cap(),
                ev_max_power_input=self.rnd_mpi(),
                battery_degradation=self.rnd_deg(),
            )

            # hold for interarrival time
            self.hold(self.rnd_iat())
            ev.register(self.evs)
            i += 1
            #
            if print_ev:
                print(f"EV {ev.name()}")
                print(f"dur {ev.dur}")
                print(f"soc {ev.soc}")
                print(f"dsc {ev.dsc}")
                print(f"cap {ev.cap}")
                print(f"mpi {ev.mpi}")
                print(f"deg {ev.deg}")
                print(" \n")


class SE_Generator(sim.Component):
    """Class to model the behaviour of Supply Equipment (SE).

    Args:
        number_of_ses (int): Number of SEs to be generated.
        number_of_con (int): Number of SEs connected to the grid.
    """

    def setup(self, number_of_ses, number_of_con):
        self.nse = number_of_ses
        self.ncn = number_of_con
        self.ses = []

        self.rnd_mpo = create_random_generator(params_dict, "MPO")

    def process(self):
        i = 1
        while i <= self.nse:
            se = SE(se_max_power_output=self.rnd_mpo(), connected_to_grid=LAY[i - 1])
            se.register(self.ses)
            i += 1


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

app = sim.App(
    trace=False,  #                    defines whether to trace or not
    random_seed=random_seed,  #        if “*”, a purely random value (based on the current time)
    time_unit=time_unit,  #            defines the time unit used in the simulation
    name="Tetris Game Charger",  #     name of the simulation
    do_reset=True,  #                  defines whether to reset the simulation when the run method is called
    yieldless=True,  #                 defines whether the simulation is yieldless or not
)

app.number_balked = 0
app.number_reneged = 0

# Create Queue and set monitor to stats_only
QUE = sim.Queue("waiting_line")
# https://www.salabim.org/manual/Queue.html
QUE.length_of_stay.monitor(value=True)
QUE.length_of_stay.reset_monitors(stats_only=True)

HUB = SE_Generator(number_of_ses=m, number_of_con=c)
GEN = EV_Generator(number_of_evs=e)
TGC = TGC(name="Tetris Game Charger")

# Execute Simulation
app.run(till=sim_time)

# --------------------------------------------------------------------------
# Reporting Results
# --------------------------------------------------------------------------

print("\n")
QUE.length_of_stay.print_statistics()
print(f"Wq: = {QUE.length_of_stay.mean()}\n")

print("\nEV Statistics:")
# for ev in GEN.evs:
#     # print(f"\n{ev.name()}")
#     print(
#         f"""{ev.name()}\t \
#           tot: {round(ev.mon_kwh.duration(ex0=True) * ev.mon_kwh.mean(ex0=True), 2)} kWh\t \
#           dur: {round(ev.mon_kwh.duration(ex0=False), 2)} hrs\t \
#           avg: {round(ev.mon_kwh.mean(ex0=False), 2)} kWh\t \
#           soc: {round(ev.state_of_charge/ev.cap, 2)} %"""
#     )
# ev.mon_kwh.print_statistics()
# ev.mon_dur.print_statistics()
# print(ev.mon_kwh.as_dataframe())

# print(
#     f"{ev.name()} - dsc: {ev.dsc} - csc: {ev.csc} - toa: {ev.toa} - tod: {ev.tod}"
# )

# TODO
# cus_mon = sum(ev.mon_kwh for ev in GEN.evs).rename('Customer Satisfaction')
# # cus_mon.print_statistics()
# print(f"cus_mon.name(): {round(cus_mon.mean(), 2)} %")

print("\nSE Statistics:")

for se in HUB.ses:
    # print(f"\n{se.name()}")
    print(
        f"""{se.name()}\t \
          tot: {round(se.mon_kwh.duration(ex0=False) * se.mon_kwh.mean(ex0=False), 2)} kWh\t \
          dur: {round(se.mon_kwh.duration(ex0=False), 2)} hrs\t \
          avg: {round(se.mon_kwh.mean(ex0=False), 2)} kWh\t \
          utl: {round(se.utilization, 2)} %"""
    )

    # se.mon_kwh.print_statistics()
    # se.mon_dur.print_statistics()
    # print(se.mon_kwh.as_dataframe())

enx_mon = sum(se.mon_kwh for se in HUB.ses).rename('Enexis performance')
# enx_mon.print_statistics()
print(f"Enexis Grid Utilization: {round(enx_mon.mean()/EX_MPO, 2)} %")

print(f"\nEVs balked: {app.number_balked}")
print(f"EVs reneged: {app.number_reneged}")


# soc calcualtion needs the start soc bij opgeteld te wroden TODO
# check als charge less than dureation TODO
# total % for all SE Enexis
# total CSAT for all EV
