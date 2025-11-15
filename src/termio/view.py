from models.player import PlayerUnit
#from cards.enums import ManaType, CardType
from .color import TCol

class TerminalView:
    """
    Handles rendering game state to the terminal.
    """
    @staticmethod
    def get_player_status_string(player: PlayerUnit, bold=False) -> str:
        """Formats a multi-line string for the player's active monster and mana."""
        if not player.active_monster:
            return "No active monster."
        
        header = f"{TCol.HEADER}{TCol.BOLD if bold else ''}{player.active_monster.title}\t\tHP {player.active_monster.health}{TCol.ENDC}"
        mana_pool = TerminalView.get_mana_pool_string(player.active_monster)
        return f"{header}\t{mana_pool}"

    @staticmethod
    def get_mana_pool_string(player: PlayerUnit) -> str:
        """Returns the player's current mana pool as a formatted string."""
        pool_parts = [f"{TCol.OKBLUE}{v}{k.value[:1].upper()}{k.value[1:2].lower()}{TCol.ENDC}" 
                      for k, v in player.mana_pool.items() if v > 0]
        return " ".join(pool_parts) if pool_parts else "No mana"
    
    @staticmethod
    def get_hand_list_string(player: PlayerUnit) -> str:
        """Returns the player's current hand as a formatted string."""
        if not player.hand:
            return "Your hand is empty."
        hand_strings = []
        for hand_index, card in enumerate(player.hand, start=1):
            hand_strings.append(f"[{hand_index}]: {card.title}\t{card.type.value.upper()}")
        return "\n".join(hand_strings)