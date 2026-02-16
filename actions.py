import random
from abc import ABC, abstractmethod


class Action(ABC):
    """Abstract base class for all player actions."""

    @abstractmethod
    def execute(self, player, target=None):
        pass


class AttackAction(Action):
    """Perform a basic attack on a target. Damage = attacker power - target defense."""

    def execute(self, attacker, target=None):
        if target is None:
            print("No target selected!")
            return

        # Speed-based dodge chance
        dodge_chance = target.speed / 100
        if random.random() < dodge_chance:
            print(f"{target.name} dodges the attack!")
            return

        damage = max(0, attacker.attack_power - target.defense)
        target.hp -= damage
        print(f"{attacker.name} attacks {target.name} for {damage} damage!")
        if target.hp <= 0:
            print(f"{target.name} has been eliminated!")


class DefendAction(Action):
    """Double the player's defense for the current turn."""

    def execute(self, player, target=None):
        original_defense = player.defense
        player.set_defending()  # Uses the new method that tracks defending state
        print(f"{player.name} defends, increasing defense from {original_defense} to {player.defense}!")


class SpecialMoveAction(Action):
    """Execute the player's unique special move if not on cooldown."""

    def execute(self, player, target=None):
        if player.special_move_cooldown == 0:
            player.special_move(target)
        else:
            print(f"{player.name}'s special move is on cooldown for {player.special_move_cooldown} more turns.")
