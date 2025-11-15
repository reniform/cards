from models.player import PlayerUnit
from cards.enums import ManaType
from .color import TCol

class TerminalView:
    """
    Handles rendering game state to the terminal.
    """
    @staticmethod
    def get_player_status_string(player: PlayerUnit) -> str:
        """Formats a multi-line string for the player's active monster and mana."""
        if not player.active_monster:
            return "No active monster."
        
        header = f"{TCol.HEADER}{player.active_monster.title}\t\t HP {player.active_monster.health}{TCol.ENDC}"
        mana_pool = TerminalView.get_mana_pool_string(player)
        return f"{header}\n{mana_pool}"

    @staticmethod
    def get_mana_pool_string(player: PlayerUnit) -> str:
        """Returns the player's current mana pool as a formatted string."""
        pool_parts = [f"{TCol.OKBLUE}{k.value[:1].upper()}{k.value[1:2].lower()}{v}{TCol.ENDC}" 
                      for k, v in player.mana_pool.items() if v > 0]
        return " ".join(pool_parts) if pool_parts else "No mana"