import salabim as sim
import numpy as np


class tick(sim.Component):
    def process(self):
        while True:
            self.hold(0.5, priority=0)
            print(f"tick: {env.now()}")


class Mon0(sim.Component):
    def setup(self):
        self.mon = sim.Monitor("monitor", level=True, initial_tally=2)

    def process(self):
        i = 1
        while i < 3:
            print(f"1: {env.now()}\ti: {i}")
            self.hold(i, priority=0)
            print(f"2: {env.now()}\ti: {i}")
            self.mon.tally(i)
            i += 1
        while i > 2 and i < 6:
            print(f"3: {env.now()}\ti: {i}")
            self.hold(i)
            print(f"4: {env.now()}\ti: {i}")
            self.mon.tally(i)
            i += 1

        self.mon.tally(0)
        self.mon.print_statistics()
        df = self.mon.as_dataframe()
        df["t2"] = df["t"].shift(-1)
        df["dt"] = df["t2"] - df["t"]
        df["v1"] = df["dt"] * df["monitor.x"]
        print(df)
        tot = np.nansum(df["v1"])
        dur = self.mon.duration()
        dr0 = self.mon.duration_zero()
        print(tot, tot / dur, tot / dr0)


class Mon1(sim.Component):
    def setup(self):
        self.mon = sim.Monitor("monitor", level=True, initial_tally=2)

    def process(self):
        i = 0
        print(env.now())
        self.hold(1)
        print(env.now())
        while i < 5:
            print(env.now())
            self.hold(i)
            print(env.now())
            self.mon.tally(i)
            i += 1
        self.mon.tally(0)
        self.mon.print_statistics()
        print(self.mon.as_dataframe())


class Mon2(sim.Component):
    def setup(self):
        self.mon = sim.Monitor("monitor", level=True, initial_tally=2)

    def process(self):
        k = 0
        while k < 2:
            i = 0
            self.hold(1)
            while i < 5:
                print(env.now())
                self.hold(i)
                print(env.now())
                self.mon.tally(i)
                i += 1
            self.mon.tally(0)
            self.mon.print_statistics()
            print(self.mon.as_dataframe())
            k += 1


class Mon3(sim.Component):
    def setup(self):
        self.mon = sim.Monitor("pwr", level=True, initial_tally=0)

    def process(self):
        i = 1
        while i < 4:
            print(f"1: {env.now()}\ti: {i}")
            self.hold(i + 0.2, priority=0)
            print(f"2: {env.now()}\ti: {i}")
            self.mon.tally(i)
            # print(f"m1: {self.mon()*self.mon.t()}")
            # print(f"m3: {self.mon.t()}")
            # print(f"m4: {self.mon.xduration()}")
            # print(f"m5: {self.mon.xt()}")
            # print(f"m6: {self.mon.tx()}")
            i += 1

        self.mon.tally(0)
        self.mon.print_statistics()
        df = self.mon.as_dataframe()
        df["t2"] = df["t"].shift(-1)
        df["dt"] = df["t2"] - df["t"]
        df["cap"] = df["dt"] * df["pwr.x"]
        tot = np.nansum(df["cap"])

        cap = (
            self.mon.as_dataframe()
            .assign(
                t2=df["t"].shift(-1),
                dt=lambda df: df["t2"] - df["t"],
                cap=lambda df: df["dt"] * df["pwr.x"],
            )["cap"]
            .sum(skipna=True)
        )

        dur = self.mon.duration()
        dr0 = self.mon.duration_zero()
        print(cap, tot, tot / dur, tot / dr0)


env = sim.Environment(trace=False)

Mon3()

env.run()
