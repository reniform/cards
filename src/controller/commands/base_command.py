from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game import GameState, GameController


class Command(ABC):
    """
    Abstract base class for all game commands.

    This class defines the interface that all concrete command objects
    must implement. The GameController will interact with these objects.
    """

    @abstractmethod
    def execute(self, game_state: "GameState", controller: "GameController") -> tuple[bool, bool]:
        """
        Executes the command. This method should modify the game state according
        to the specific implementation of the command.

        Args:
            game_state (GameState): The current state of the game.

        Returns:
            A tuple (turn_ended, needs_redraw) indicating the outcome.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        attrs = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
