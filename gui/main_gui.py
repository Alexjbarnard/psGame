# gui/main_gui.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
from kivy.lang import Builder
import threading
import time

# Use absolute imports now that the project root is on the path
from core.game_engine import PitStopGame
from core.save_manager import save_game, load_game

# Register a font to use for Font Awesome icons
LabelBase.register(
    name='fontawesome',
    fn_regular='assets/fonts/Font Awesome 7 Free-Solid-900.otf'
)


class MainScreen(BoxLayout):
    """
    The main game screen layout.
    """
    # Define properties to automatically update the UI when they change
    currency_text = StringProperty("Currency: $0")
    income_text = StringProperty("Income: $0/s")
    version_info = StringProperty("")  # New property for the version number

    def __init__(self, game, settings, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.settings = settings
        self.version_info = f"v{self.settings['version_number']}"
        self.update_ui()

    def update_ui(self, dt=None):
        """
        Method called by the Kivy clock to refresh the UI.
        This runs on the main thread and is safe for UI updates.
        """
        state = self.game.get_state()
        self.currency_text = f"Currency: ${state['currency']}"
        self.income_text = f"Income: ${int(state['income_per_second'])}/s"

        self.check_button_colors()

    def check_button_colors(self):
        """Checks if the player has enough money for each upgrade and sets button colors."""
        # Gas Pump Upgrade Button
        gas_pump_cost = self.game.upgrade_pump_cost()
        upgrade_pump_btn = self.ids.upgrade_gas_pump_btn
        upgrade_pump_btn.text = f'Upgrade (${gas_pump_cost})'
        if self.game.currency >= gas_pump_cost:
            upgrade_pump_btn.background_color = [0, 1, 0, 1]  # Green
        else:
            upgrade_pump_btn.background_color = [0.5, 0.5, 0.5, 1]  # Gray

        # Upgrade Store Button
        upgrade_store_cost = self.game.upgrade_store_cost()
        upgrade_store_btn = self.ids.upgrade_store_btn
        upgrade_store_btn.text = f'Upgrade (${upgrade_store_cost})'
        if self.game.currency >= upgrade_store_cost:
            upgrade_store_btn.background_color = [0, 1, 0, 1]
        else:
            upgrade_store_btn.background_color = [0.5, 0.5, 0.5, 1]

    # Action methods for buttons
    def buy_pump(self):
        if self.game.buy_gas_pump():
            print("New pump purchased!")
        else:
            print("Not enough currency!")
        self.update_ui()

    def upgrade_pump(self):
        if self.game.upgrade_gas_pump():
            print("Pump upgraded!")
        else:
            print("Not enough currency!")
        self.update_ui()

    def upgrade_store(self):
        if self.game.upgrade_store():
            print("Store upgraded!")
        else:
            print("Not enough currency!")
        self.update_ui()

    def remodel(self):
        self.game.remodel()
        print("Remodel complete!")
        self.update_ui()

    def prestige(self):
        self.game.prestige()
        print("Prestige complete!")
        self.update_ui()

    def save_game(self):
        save_game(self.game.get_state(), backups_to_keep=self.settings["backups_to_keep"])
        print("Game saved!")
        self.update_ui()


class PitStopApp(App):
    def __init__(self, game, settings, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.settings = settings

    def build(self):
        Builder.load_file('gui/pitstop.kv')
        Clock.schedule_interval(self.update_game_and_ui, self.settings["tick_interval"])
        return MainScreen(self.game, self.settings)

    def update_game_and_ui(self, dt):
        """Main game loop for Kivy, runs on the UI thread."""
        self.game.tick(1)
        self.root.update_ui()


def start_gui_game(game, lock, stop_event, settings):
    """Function to launch the Kivy app."""
    print("Launching Kivy GUI...")
    PitStopApp(game=game, settings=settings).run()
    print("Kivy GUI closed.")
    stop_event.set()


if __name__ == '__main__':
    from core.game_engine import PitStopGame
    from core.save_manager import save_game

    game = PitStopGame()
    lock = threading.Lock()
    stop_event = threading.Event()
    settings = {"backups_to_keep": 10, "tick_interval": 1.0, "version_number": "3.3"}
    start_gui_game(game, lock, stop_event, settings)
