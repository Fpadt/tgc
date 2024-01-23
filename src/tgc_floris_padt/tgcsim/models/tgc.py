from salabim import Component, Queue

class TGC(Component):
    """Tetris Game Charger"""

    @property
    def fac(self):
        return self._fac

    @fac.setter
    def fac(self, value):
        self._fac = value

    def setup(
        self,
        enexis_max_power_output,
        priority_rule,
        simulation_app, #TODO: remove
    ):
        # --- Objects ---
        self._fac = None
        self._mpo = enexis_max_power_output     
        self._rul = priority_rule        
        # self._app = simulation_app,
        self._ocp = Queue("OptimizedChargingPlan")

    def request_power(self):
        self.assign_power()
        return True
    
    # def set_clock(self):
    #     min_rtc = float("inf")
    #     for se in self._fac.fac:
    #         if se.evc is not None and se.evc.isscheduled():
    #             if se.evc.tcr > 0:
    #                 tst = se.scheduled_time() - self._app.now()
    #                 min_rtc = min(min_rtc, se.evc.tcr)
    #             if min_rtc <= 0:
    #                 min_rtc = float("inf")
    #     self._clock.activate()
    #     self._clock.remaining_duration(min_rtc, priority=0, urgent=True)

    def make_schedule(self, property_name):
        """Make a schedule of EVSEs sorted on property_name"""

        # new schedule
        self._ocp.clear()

        # If property_name starts with a minus sign, reverse the order
        reverse = 1
        if property_name[0] == "-":
            reverse = -1
            property_name = property_name[1:]

        # Create schedule sorted on property_name
        # add the EVSE without EV at then end to make it complete
        for se in self._fac.fac:
            if se.evc is None or se.con == False:
                property_value = float("inf")
            else:
                property_value = reverse * getattr(se.evc, property_name)
            self._ocp.add_sorted(se, property_value)

        return self._ocp

    # def print_state(self, se):
    #     if se.evc is None:
    #         None
    #         # print(f"{app.now()}\t - NO_EV/{se.name()} ")
    #     else:
    #         #   toa: {se.ev.toa} - tod: {se.ev.tod} -  \
    #         print(
    #             f"""{self.app.now()}\t{se.evc.name()}/{se.name()}\tcsc: {se.evc.sat}"""
    #             # \tpwr: {se.pwr}\tdsc: {round(se.ev.dsc)}  rem: {se.remaining_duration()}\tsch: {se.scheduled_time()}"""
    #         )

    # def print_charge(self):
    #     for se in self._fac.fac:
    #         if se.evc is not None and se.evc.isscheduled():
    #             print(se.get_charge_profile())

    def assign_power(self):
        """Assign power to EVSEs according to priority
        Start with the total Power available fro Enexis
        assign according to priority set by sorting on property
        """
        # initialize the available power to the total power available
        available_power = self._mpo

        # make a schedule
        order = self.make_schedule(self._rul)

        # assign power to EVSEs
        while len(order) > 0:
            se = order.pop()
            if se.evc == None:
                se.pwr = 0
            else:
                se.pwr = se.con * min(
                    [
                        se.mpo,
                        available_power,
                        se.evc.p_d,
                    ]
                )
                # schedule the ev for teh time required
                if not se.evc.iscurrent():
                    se.evc.remaining_duration(se.evc.t_d)

            available_power -= se.pwr
            available_power = max(available_power, 0)  
            # print(f"available_power: {available_power}")

    # def get_next_hold(self) -> float:
    #     nxt_hold = float("inf")
    #     for se in self._fac.fac:
    #         if se.evc is not None and se.evc.isscheduled():
    #             nxt_hold = min(se.get_charge_profile()["n_hold"], nxt_hold)
    #     return nxt_hold

    # def update_se_enerygy_charged(self):
    #     for se in self._fac.fac:
    #         if se.evc is not None and se.evc.isscheduled():
    #             se.update_energy_charged()

    def process(self):
        self.passivate()
        # while True:
            # ts = app.now(); print(f"time: {ts}")
        # self.update_se_enerygy_charged()
        # next_hold = self.get_next_hold()
        # ts = app.now(); print(f"time: {ts}")
        # self.hold(next_hold)
        # ts = app.now(); print(f"time: {ts}")
        # statistics
        # [self.print_state(x) for x in self._fac.fac]
        # [self.print_charge(x) for x in self._fac.fac]
        # next_hold = self.determine_next_hold()
        # self.standby()
        # self.hold(next_hold, priority=0, urgent=True)  # makes it run every hour
