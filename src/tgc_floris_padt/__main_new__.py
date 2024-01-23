# ------------------------------------------------------------------------
# Config: packages and coding import
# ------------------------------------------------------------------------

from config import *
from tgcsim.network.tgc_network import TGC_network

def enexis_plot(df):
    plt.step(df['t'], df['EV_kwh.x'], where='post', color='#DF0073')

    plt.xlabel('t')
    plt.ylabel('cap')
    plt.title('Step Plot')

    plt.show()

# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------

app = App(
    trace=False,  #                    defines whether to trace or not
    random_seed=random_seed,  #        if “*”, a purely random value (based on the current time)
    time_unit=time_unit,  #            defines the time unit used in the simulation
    name="Tetris Game Charger",  #     name of the simulation
    do_reset=True,  #                  defines whether to reset the simulation when the run method is called
    yieldless=True,  #                 defines whether the simulation is yieldless or not
)

# --------------------------------------------------------------------------
app.number_balked = 0
app.number_reneged = 0
app.evs = []

# ------------------------------------------------------------------------
# Model
# ------------------------------------------------------------------------
TGCN = TGC_network(
    enexis_max_power_output=EX_MPO,
    priority_rule=RUL,
    simulation_app=app,
    distributions_dict=params_dict,
    layout=LAY,
    number_of_evs=e,
    max_queue_length=q,
    max_wait_time=w,
)

TGCN.create_network()

# --------------------------------------------------------------------------
# Execute Simulation
sim_start = datetime.now()
app.run(till=sim_time)


# --------------------------------------------------------------------------
# Reporting Results
# --------------------------------------------------------------------------

print("\n")
TGCN.que.length_of_stay.print_statistics() 
print(f"Wq: = {TGCN.que.length_of_stay.mean()}\n")

print(f"\nEVs balked: {app.number_balked}")
print(f"EVs reneged: {app.number_reneged}")

# --- EV Statistics ---

if print_ev_details == True:
    print("\nEV Statistics:")
    for ev in app.evs:
        print(
            f"""{ev.name()}\t \
    toa: {round(ev._toa, 2)}\tdur: {round(ev._dur, 2)}\t \
    e_i: {round(ev.e_i, 2)}\te_d: {round(ev.e_d, 2)}\te_r: {round(ev.e_r, 2)}\te_c: {round(ev.e_c, 2)}\t \
    sat: {round(ev.sat, 2)} %"""
        )

    # iel: {round(ev.e_i, 2)} kWh\t \
# --- SE Statistics ---
if print_se_details == True:
    print("\nSE Statistics:")

    for se in TGCN.fac.fac:
        print(
            f"""{se.name()}\t \
            tot: {round(se.mon_kwh.duration(ex0=False) * se.mon_kwh.mean(ex0=False), 2)} kWh\t \
            dur: {round(se.mon_kwh.duration(ex0=False), 2)} hrs\t \
            avg: {round(se.mon_kwh.mean(ex0=False), 2)} kWh\t \
            utl: {round(se.utl, 2)} %"""
        )

    # se.mon_kwh.print_statistics()
    # se.mon_dur.print_statistics()
    # print(se.mon_kwh.as_dataframe())
# --- Customer Satisfaction ---
sat_values = [ev.sat for ev in app.evs]
mean_sat = np.nanmean(sat_values)

print(f"Customer Satisfaction: {round(mean_sat, 0)} %")

dfs = []
for ev in app.evs:
    # print(f"\nEV: {ev.name()}\n{ev.mon_kwh.as_dataframe()}")
    dfs.append(ev.mon_kwh.as_dataframe())

ldf=pd.DataFrame({'t': [sim_time], 'EV_kwh.x': [0]})
dfs.append(ldf)
ndf = pd.concat(dfs, ignore_index=True).groupby('t')['EV_kwh.x'].sum().reset_index()
# print(f"\nown merge: {ndf}")

# Salabim
# evs_mon = sum(ev.mon_kwh for ev in app.evs).rename("EV") 
# print(f"\nSalabim sum: {evs_mon.as_dataframe()}")


if ex_plot ==True:
    enexis_plot(ndf)




cap = ndf.assign(
            pt=ndf["t"].shift(-1),
            dt=lambda ndf: ndf["pt"] - ndf["t"],
            cp=lambda ndf: ndf["dt"] * ndf["EV_kwh.x"],
        )["cp"].sum(skipna=True)

print(f"New Enexis Grid Utilization: {round(100*cap/(EX_MPO*sim_time))} %")

# --- Enexis ---
enx_mon = sum(se.mon_kwh for se in TGCN.fac.fac).rename("Enexis performance")
# enx_mon.print_statistics()

dlv = enx_mon.duration(ex0=False) * enx_mon.mean(ex0=False)
pot = enx_mon.duration(ex0=False) * (EX_MPO - enx_mon.mean(ex0=False))
utl = dlv / (dlv + pot)

print(
    f"""
      Enexis Grid Utilization: {round(100*utl)} %\t\
      Energy Delivered: {round(dlv, 2)} kWh\t\
      missed to deliver: {round(pot, 2)} kWh"""
)

print(f"\nSimulation time: {datetime.now() - sim_start}")

# --- Plot ---
dfRaw = enx_mon.as_dataframe()
dfRaw = dfRaw.rename(columns={"enxpwr": "B"})
dfResult = dfRaw.round(2)
dfResult.to_csv(
    "time"
    + str(sim_time)
    + "_enx_c"
    + str(c)
    + "_q"
    + str(q)
    + "_r"
    + str(r)
    + "_.csv",
    index=False,
    header=True,
    sep=";",
    decimal=".",
)

# df = enx_mon.as_dataframe()
# plt.step(df['t'], df['Enexis performance.x'], where='post')

# plt.xlabel('t')
# plt.ylabel('cap')
# plt.title('Step Plot')

# plt.show()

# TODO: check coding in EV generator for dsc and isc
# TODO:  check als tch charge less than duration ??
# TODO: ev.mpi formule > 80% 
# TODO: OLP koppelen aan TGC

