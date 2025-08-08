"""
CLI version of the Pit Stop game.
Handles text-based interaction for testing.
"""

def start_cli_game():
    print("CLI Game Started!")
    print("Type 'quit' to exit.")

    running = True
    while running:
        command = input("> ").strip().lower()
        if command == "quit":
            running = False
            print("Thanks for playing Pit Stop!")
        else:
            print(f"You entered: {command}")

