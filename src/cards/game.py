from .models import PlayerMonState

player = PlayerMonState('Insipid Atom', 50, 20)
opponent = PlayerMonState('Petulant Beast', 60, 5)

def main():
    while True:
        print(f'{player.title} \t\t HP {player.health}')
        player.print_mana_pool()
        print(f'{opponent.title} \t\t HP {opponent.health}')
        command = input("What will you do? :D ")
        # RUN INPUT TURN
        match command.split():
            case ['attack']:
                player.use_attack(0, opponent)
            case ['mana', manaType]:
                player.add_mana(manaType, 1)
            case ['mana', manaType, qty]:
                player.add_mana(manaType, int(qty))
            case ['debug']:
                break
            case ["exit"]:
                print("Okay.")
                exit()
            case _:
                print("??? What???")
        
        # PERFORM CHECKS
        if opponent.health <= 0:
            print("You win!")
            exit()