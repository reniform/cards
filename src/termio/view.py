from models.player import PlayerUnit
from core.enums import CardType, StageType
from enum import Enum
import colorful as cf
import os


class ManaColor(Enum):
    GRASS       = cf.forestGreen
    FIRE        = cf.red
    WATER       = cf.deepSkyBlue
    LIGHTNING   = cf.goldenrod
    FIGHTING    = cf.sienna
    PSYCHIC     = cf.mediumPurple
    DARKNESS    = cf.steelBlue
    METAL       = cf.darkSlateGray
    DRAGON      = cf.oliveDrab
    FAIRY       = cf.hotPink
    COLORLESS   = cf.beige

class TerminalView:
    """
    Handles rendering game state to the terminal.
    """
    @staticmethod
    def get_mana_pool_string(monster) -> str:
        """Returns the monster's current mana pool as a formatted string."""
        # Use the total_mana property which includes attached mana cards.
        pool_parts = [f"{ManaColor[k.name].value}{v}{k.value[:1].upper()}{k.value[1:2].lower()}{cf.reset}"
                      for k, v in monster.total_mana.items() if v > 0]
        return " ".join(pool_parts) if pool_parts else ""

    @staticmethod
    def print_game_header() -> str:
        pass

    @staticmethod
    def print_player_data(player, opposite=False) -> str:
        # Pad the player title to 12 characters.
        padded_title = f"{player.title.upper():<11}"

        # Draw the prize cards, of symbol [].
        prize_sprite = '[]'
        score = len(player.prize)
        prize_groups = []
        # Draw the prize cards in groups of two.
        while score > 0:
            if score >= 2:
                prize_groups.append(prize_sprite * 2)
                score -= 2
            else:
                prize_groups.append(prize_sprite)
                score -= 1
        padded_prize = " ".join(prize_groups)

        # Assemble the parts.
        parts = [
            f"{cf.bold}{cf.red if opposite else cf.white}{padded_title}{cf.reset}",
            f"{cf.tomato}in deck{cf.reset}: {len(player.deck)}",
            f"{cf.tomato}in hand{cf.reset}: {len(player.hand)}",
            f"{cf.tomato}in discard{cf.reset}: {len(player.discard)}",
            f"{cf.gold}{padded_prize}{cf.reset}"
        ]
        return "  ".join(parts)

    def print_bench() -> str:
        pass

    @staticmethod
    def print_active_monster(player, Bold=False) -> str:
        if not player.active_monster:
            return "\t(No active monster)"

        # The player's active monster type, always two characters.
        active_mon_mana_type = player.active_monster.card.mana_type.value[:1].upper() + player.active_monster.card.mana_type.value[1:2].lower()
        # The player's active monster stage, always one character.
        match player.active_monster.card.stage:
            case StageType.BASIC:
                active_mon_stage = 'B'
            case StageType.STAGEONE:
                active_mon_stage = '1'
            case StageType.STAGETWO:
                active_mon_stage = '2'
        # The player's active monster id, padded for space.
        padded_id = f"{player.active_monster.id:03d}"
        # The player's active monster title, padded for space.
        active_mon_title = f"{player.active_monster.card.title:<12}"
        # The player's active monster health and max health.
        active_mon_health = f"{player.active_monster.health:3d}"
        active_mon_max_health = f"{player.active_monster.card.health:3d}"
        # The player's status
        # TODO IMPLEMENT STATUS EFFECTS
        
        parts = [
            "\t",
            f"{ManaColor[player.active_monster.card.mana_type.name].value}{active_mon_mana_type}{cf.reset}",
            f"{active_mon_stage} [{cf.darkSlateGray}{padded_id}{cf.reset}]",
            f"{ManaColor[player.active_monster.card.mana_type.name].value}{cf.bold if Bold else ''}{active_mon_title}{cf.reset}",
            f"{active_mon_health}/{active_mon_max_health}",
            f"{TerminalView.get_mana_pool_string(player.active_monster)}"
        ]
        return " ".join(parts)
    
    @staticmethod 
    def print_hand(player) -> str:
        if not player.hand:
            return "Your hand is empty."

        try:
            max_width = os.get_terminal_size().columns
        except OSError:
            max_width = 80  # Fallback for environments where terminal size can't be determined

        lines = []
        current_line = []
        current_length = 0
        separator = " | "

        for card_id, hand_card in player.hand.items():
            # Determine the color based on the card type
            if hand_card.card.type == CardType.MONSTER:
                color = ManaColor[hand_card.card.mana_type.name].value
            elif hand_card.card.type == CardType.MANA:
                color = ManaColor[hand_card.card.mana_type.name].value
            else:
                color = cf.white

            # Format the card string
            card_str_visible = f"[{card_id}] {hand_card.card.title}"
            card_str_formatted = f"{color}{card_str_visible}{cf.reset}"

            # Check if adding the new card exceeds the line width
            if current_line and current_length + len(separator) + len(card_str_visible) > max_width:
                lines.append(separator.join(current_line))
                current_line = []
                current_length = 0

            current_line.append(card_str_formatted)
            current_length += len(card_str_visible) + (len(separator) if current_line else 0)

        if current_line:
            lines.append(separator.join(current_line))

        return "\n".join(lines)

    @staticmethod
    def print_prompt(player: PlayerUnit) -> str:
        parts = ["== actions:"]

        # Add commands that are always available during a player's turn
        parts.append("pass | view [id] | show hand | exit")

        # Activation is available when there is no active monster
        if not player.active_monster:
            parts.append("| activate")
        else:
            # These actions require an active monster
            parts.append("| bench | evolve | attach | use | retreat | ability | attack")
            
        return " ".join(parts)

    @staticmethod
    def get_player_status_string(player: PlayerUnit, bold=False) -> str:
        """Formats a multi-line string for the player's active monster and mana."""
        if not player.active_monster:
            return "No active monster."
        
        #header = f"{TCol.HEADER}{TCol.BOLD if bold else ''}{player.active_monster.card.title} {player.active_monster.card.id} \t\tHP {player.active_monster.health}{TCol.ENDC}"
        mana_pool = TerminalView.get_mana_pool_string(player.active_monster)
        return f"header\t{mana_pool}"

    @staticmethod
    def get_hand_list_string(player: PlayerUnit) -> str:
        """Returns the player's current hand as a formatted string."""
        if not player.hand:
            return "Your hand is empty."
        hand_strings = []
        for card_id, card in player.hand.items():
            hand_strings.append(f"[{card_id}] {card.card.title}\t{card.card.type.value.upper()}")
        return "\n".join(hand_strings)