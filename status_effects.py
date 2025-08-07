from abc import ABC, abstractmethod

# Purpose: Framework for status effects
class StatusEffect(ABC):
    def __init__(self, duration):
        self.duration = duration # how long effect lasts

    # All subclasses impement own apply method
    @abstractmethod
    def apply(self, character):
        pass
    # Purpose: Decrements effect duration
    def decrement_duration(self):
        self.duration -= 1
        return self.duration > 0

# Purpose: Creates a Poison Effect
# Implements the abstract StatusEffect class
class PoisonEffect(StatusEffect):
    def __init__(self, damage_per_turn, duration):
        super().__init__(duration)
        self.damage_per_turn = damage_per_turn # hp lost per turn
    # Purose: Applies the Poison effect on character
    def apply(self, character):
        character.hp -= self.damage_per_turn # character hp is set to the damage taken per turn
        print(f"{character.name} is poisoned and loses {self.damage_per_turn} HP! ({character.hp} HP left)")

# Purpose: Creates the stun effect
# Impements the abstract StatusEffect class
class StunEffect(StatusEffect):
    def __init__(self, duration):
        super().__init__(duration)
    # Applies the stun effect on chosen character
    def apply(self, character):
        print(f"{character.name} is stunned and cannot act this turn!")

# Purpsose: Boosts the defense of character
class DefenseBoostEffect(StatusEffect):
    def __init__(self, defense_increase, duration):
        super().__init__(duration) # how long it lasts
        self.defense_increase = defense_increase # increases characters defense

# Purpose: Applies the defense boost
    def apply(self, character):
        # Adds defense to character
        character.defense += self.defense_increase
        print(f"{character.name} gains {self.defense_increase} extra defense for {self.duration} turns!")

