import os
from termio.view    import TerminalView
from termio.termio  import CommandHandler
import colorful as cf

class GameState:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.turn_count = 1

    def run(self):
        """
        The main game loop.
        """
        self.redraw_screen()  # Draw the initial screen once.
        while True:

            command = input(f"[{self.player.title}] perform an action! ==> ")

            parts = command.split()
            if not parts:
                continue

            command_word = parts[0]
            args = parts[1:]

            if command_word == 'debug': # Special case to break the loop
                break
            elif handler := CommandHandler.COMMANDS.get(command_word):
                # Pass the whole game state to the handler
                turn_ended, needs_redraw = handler(self, *args)
                if turn_ended:
                    input("\nPress Enter to end your turn...")
                    self.next_turn()
                    self.redraw_screen()  # Redraw for the new turn.
                elif needs_redraw:
                    self.redraw_screen()

            else:
                print("??? What???")
        
            # PERFORM CHECKS
            if self.opponent.active_monster and self.opponent.active_monster.health <= 0:
                print("You win!")
                os._exit(1)

    def next_turn(self):
        """
        Handles all end-of-turn and start-of-turn logic.
        """
        # Swap player and opponent
        # self.player, self.opponent = self.opponent, self.player
        self.turn_count += 1
        # TODO: Implement start-of-turn card draw
        self.player.draw_from_deck(1)

    def redraw_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'\n== {cf.bold} Turn [{self.turn_count}] {cf.reset} ======================================================================')
        print(TerminalView.print_player_data(self.opponent, opposite=True))
        print(TerminalView.print_active_monster(self.opponent))
        print(TerminalView.print_active_monster(self.player, Bold=True))
        print(TerminalView.print_player_data(self.player))
        print(TerminalView.print_hand(self.player))
        print(TerminalView.print_prompt(self.player))