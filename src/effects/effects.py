from abc import ABC, abstractmethod


class Effect(ABC):
    """
    Abstract base class for all effects in the game.
    """

    @abstractmethod
    def apply(self, attacker, target):
        """
        Applies the effect to the target.
        """
        pass