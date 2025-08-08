# gui/gui_main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty
import threading
import time

# Import the real game engine and save manager
from core.game_engine import PitStopGame
from core.save_manager import save_game, load_game


class MainScreen(BoxLayout):
    """
    The main game screen layout.
    """
    # Define properties to automatically update the UI when they change
    currency_text = StringProperty("Currency: $0.00")
    income_text = StringProperty("Income: $0.00/s")
    stats_text = StringProperty("")

    def __init__(self, game, lock, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 20
        self.spacing = 10
        self.game = game
        self.lock = lock

        # Create UI elements
        self.add_widget(Label(text="Pit Stop", font_size='48sp', size_hint_y=0.2))

        # Display current stats
        self.currency_label = Label(text=self.currency_text, font_size='24sp')
        self.income_label = Label(text=self.income_text, font_size='24sp')
        self.add_widget(self.currency_label)
        self.add_widget(self.income_label)

        # Container for action buttons
        button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.6)
        button_layout.add_widget(Button(text="Buy New Gas Pump", on_release=self.buy_pump))
        button_layout.add_widget(Button(text="Upgrade Gas Pump", on_release=self.upgrade_pump))
        button_layout.add_widget(Button(text="Upgrade Store", on_release=self.upgrade_store))
        button_layout.add_widget(Button(text="Remodel (Soft Reset)", on_release=self.remodel))
        button_layout.add_widget(Button(text="Prestige (Hard Reset)", on_release=self.prestige))
        button_layout.add_widget(Button(text="Save Game", on_release=self.save_game))

        self.add_widget(button_layout)

        self.stats_label = Label(text=self.stats_text, font_size='16sp', size_hint_y=0.2)
        self.add_widget(self.stats_label)

        self.update_ui()

    def update_ui(self, dt=None):
        """
        Method called by the Kivy clock to refresh the UI.
        This runs on the main thread and is safe for UI updates.
        """
        with self.lock:
            state = self.game.get_state()
            self.currency_label.text = f"Currency: ${state['currency']:.2f}"
            self.income_label.text = f"Income: ${state['income_per_second']:.2f}/s"

            self.stats_label.text = (
                f"Pumps: {state['gas_pumps']} (Lvl {state['gas_pump_level']})\n"
                f"Store Level: {state['store_level']}\n"
                f"Remodels: {state['remodel_count']} (Bonus: {state['remodel_multiplier']:.2f}x)\n"
                f"Prestige: {state['prestige_count']} (Bonus: {state['prestige_multiplier']:.2f}x)"
            )

    # Action methods for buttons
    def buy_pump(self, instance):
        with self.lock:
            if self.game.buy_gas_pump():
                print("New pump purchased!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def upgrade_pump(self, instance):
        with self.lock:
            if self.game.upgrade_gas_pump():
                print("Pump upgraded!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def upgrade_store(self, instance):
        with self.lock:
            if self.game.upgrade_store():
                print("Store upgraded!")
            else:
                print("Not enough currency!")
        self.update_ui()

    def remodel(self, instance):
        with self.lock:
            self.game.remodel()
            print("Remodel complete!")
        self.update_ui()

    def prestige(self, instance):
        with self.lock:
            self.game.prestige()
            print("Prestige complete!")
        self.update_ui()

    def save_game(self, instance):
        with self.lock:
            # We will use the save function from main.py's settings
            settings = {"backups_to_keep": 10}  # Placeholder until we pass it in properly
            save_game(self.game.get_state(), backups_to_keep=settings["backups_to_keep"])
            print("Game saved!")
        self.update_ui()


class PitStopApp(App):
    def __init__(self, game, lock, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.lock = lock

    def build(self):
        # We use a Clock.schedule_interval to call game.tick() and update the UI
        # We will not use the threading model from main.py
        Clock.schedule_interval(self.update_game_and_ui, 1.0)
        return MainScreen(self.game, self.lock)

    def update_game_and_ui(self, dt):
        """Main game loop for Kivy, runs on the UI thread."""
        with self.lock:
            self.game.tick(1)
        self.root.update_ui()


def start_gui_game(game, lock, stop_event):
    """Function to launch the Kivy app."""
    # When using Kivy's clock, we don't need a separate passive income loop thread.
    # We should stop the existing threads from main.py if they are running.
    print("Launching Kivy GUI...")
    PitStopApp(game=game, lock=lock).run()
    print("Kivy GUI closed.")
    # Kivy's run() method blocks, so cleanup happens after it returns.
    stop_event.set()


if __name__ == '__main__':
    # This block is for testing the GUI in isolation
    from core.game_engine import PitStopGame

    game = PitStopGame()
    lock = threading.Lock()
    stop_event = threading.Event()
    start_gui_game(game, lock, stop_event)
