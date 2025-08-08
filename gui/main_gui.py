# gui/main_gui.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty
import threading
import time

# Use absolute imports now that the project root is on the path
from core.game_engine import PitStopGame
from core.save_manager import save_game, load_game


class MainScreen(BoxLayout):
    """
    The main game screen layout.

    All UI layout is now defined in gui/pitstop.kv. This class
    is responsible for connecting the UI to the game logic.
    """
    # Define properties to automatically update the UI when they change
    currency_text = StringProperty("Currency: $0.00")
    income_text = StringProperty("Income: $0.00/s")
    stats_text = StringProperty("")

    def __init__(self, game, lock, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.lock = lock
        self.update_ui()

    def update_ui(self, dt=None):
        """
        Method called by the Kivy clock to refresh the UI.
        This runs on the main thread and is safe for UI updates.
        """
        with self.lock:
            state = self.game.get_state()
            self.currency_text = f"Currency: ${state['currency']:.2f}"
            self.income_text = f"Income: ${state['income_per_second']:.2f}/s"

            self.stats_text = (
                f"Pumps: {state['gas_pumps']} (Lvl {state['gas_pump_level']})\n"
                f"Store Level: {state['store_level']}\n"
                f"Remodels: {state['remodel_count']} (Bonus: {state['remodel_multiplier']:.2f}x)\n"
                f"Prestige: {state['prestige_count']} (Bonus: {state['prestige_multiplier']:.2f}x)"
            )

    # Action methods for buttons
    def buy_pump(self):
        with self.lock:
            if self.game.buy_gas_pump():
                print("New pump purchased!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def upgrade_pump(self):
        with self.lock:
            if self.game.upgrade_gas_pump():
                print("Pump upgraded!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def upgrade_store(self):
        with self.lock:
            if self.game.upgrade_store():
                print("Store upgraded!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def remodel(self):
        with self.lock:
            self.game.remodel()
            print("Remodel complete!")
        self.update_ui()

    def prestige(self):
        with self.lock:
            self.game.prestige()
            print("Prestige complete!")
        self.update_ui()

    def save_game(self):
        with self.lock:
            # Placeholder until we pass settings from main.py
            settings = {"backups_to_keep": 10}
            save_game(self.game.get_state(), backups_to_keep=settings["backups_to_keep"])
            print("Game saved!")
        self.update_ui()


class PitStopApp(App):
    def __init__(self, game, lock, settings, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.lock = lock
        self.settings = settings

    def build(self):
        Clock.schedule_interval(self.update_game_and_ui, self.settings["tick_interval"])
        return MainScreen(self.game, self.lock)

    def update_game_and_ui(self, dt):
        """Main game loop for Kivy, runs on the UI thread."""
        with self.lock:
            self.game.tick(1)
        self.root.update_ui()


def start_gui_game(game, lock, stop_event, settings):
    """Function to launch the Kivy app."""
    print("Launching Kivy GUI...")
    PitStopApp(game=game, lock=lock, settings=settings).run()
    print("Kivy GUI closed.")
    stop_event.set()


if __name__ == '__main__':
    # This block is for testing the GUI in isolation
    from core.game_engine import PitStopGame
    from core.save_manager import save_game

    game = PitStopGame()
    lock = threading.Lock()
    stop_event = threading.Event()
    settings = {"backups_to_keep": 10, "tick_interval": 1.0}
    start_gui_game(game, lock, stop_event, settings)
