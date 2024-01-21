from salabim import Component

from tgcsim.models.se import SE
from tgcsim.models.distr_func_factory import create_random_generator

class SE_Generator(Component):
    """Class to model the behaviour of Supply Equipment (SE).

    Args:
        number_of_ses (int): Number of SEs to be generated.
        number_of_con (int): Number of SEs connected to the grid.
    """

    def setup(
        self,
        distributions_dict,
        layout,
        tetris_game_charger,
        waiting_line,
        simulation_app,
    ):
        # --- Constants ---
        self._dis = distributions_dict
        self._lay = layout
        self._tgc = tetris_game_charger
        self._que = waiting_line
        self._app = simulation_app
        # --- Variables ---
        self._ses = []

        self._mpo = create_random_generator(self._dis, "MPO")

    @property
    def ses(self):
        return self._ses

    def process(self):
        i = 1
        while i <= len(self._lay):
            se = SE(
                se_max_power_output=self._mpo(),
                connected_to_grid=self._lay[i - 1],
                tetris_game_charger=self._tgc,
                waiting_line=self._que,
                simulation_app=self._app,
            )
            se.register(self._ses)
            i += 1
