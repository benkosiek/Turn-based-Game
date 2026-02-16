from abc import ABC, abstractmethod


class StatusEffect(ABC):
    """Abstract base class for all status effects."""

    def __init__(self, duration):
        self.duration = duration

    @abstractmethod
    def apply(self, character):
        """Apply the effect each turn."""
        pass

    def on_expire(self, character):
        """Called when the effect expires. Override to clean up."""
        pass

    def decrement_duration(self):
        """Decrement duration and return True if the effect is still active."""
        self.duration -= 1
        return self.duration > 0


class PoisonEffect(StatusEffect):
    """Deals damage to the character each turn."""

    def __init__(self, damage_per_turn, duration):
        super().__init__(duration)
        self.damage_per_turn = damage_per_turn

    def apply(self, character):
        character.hp -= self.damage_per_turn
        print(f"{character.name} is poisoned and loses {self.damage_per_turn} HP! ({character.hp} HP left)")


class StunEffect(StatusEffect):
    """Prevents the character from acting for the duration."""

    def __init__(self, duration):
        super().__init__(duration)

    def apply(self, character):
        print(f"{character.name} is stunned and cannot act this turn!")


class DefenseBoostEffect(StatusEffect):
    """Temporarily increases a character's defense, then removes the bonus on expiry."""

    def __init__(self, defense_increase, duration):
        super().__init__(duration)
        self.defense_increase = defense_increase
        self.applied = False

    def apply(self, character):
        # Only add defense once when the effect first activates
        if not self.applied:
            character.defense += self.defense_increase
            self.applied = True
        print(f"{character.name} has +{self.defense_increase} extra defense ({self.duration} turn(s) remaining).")

    def on_expire(self, character):
        """Remove the defense bonus when the effect wears off."""
        character.defense -= self.defense_increase
        print(f"{character.name}'s defense boost has worn off. Defense back to {character.defense}.")
