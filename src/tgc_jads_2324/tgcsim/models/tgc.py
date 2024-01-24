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
    ):
        # --- Objects ---
        self._fac = None
        self._mpo = enexis_max_power_output     
        self._rul = priority_rule        
        self._ocp = Queue("OptimizedChargingPlan")

    def request_power(self):
        self.assign_power()
        return True
    
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
                # schedule the ev for the time required
                if not se.evc.iscurrent():
                    se.evc.remaining_duration(se.evc.t_d)

            available_power -= se.pwr
            available_power = max(available_power, 0)  

    def process(self):
        self.passivate()

