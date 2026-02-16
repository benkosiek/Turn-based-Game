import random
from abc import ABC, abstractmethod
from status_effects import StunEffect, PoisonEffect, DefenseBoostEffect


class Character(ABC):
    """Abstract base class defining shared attributes and behavior for all characters."""

    def __init__(self, name, hp, attack_power, defense, speed=15, is_aoe=False, target_type="enemy"):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.defense = defense
        self.base_defense = defense  # Stored so defend can be reset each turn
        self.special_move_cooldown = 0
        self.status_effects = []
        self.is_aoe = is_aoe
        self.target_type = target_type
        self.speed = speed
        self._defending = False  # Tracks whether the defend action is active this turn

    @abstractmethod
    def special_move(self, target):
        pass

    def take_damage(self, damage):
        """Reduce HP by damage minus defense (minimum 0)."""
        actual_damage = max(0, damage - self.defense)
        self.hp -= actual_damage
        print(f"{self.name} takes {actual_damage} damage! Remaining HP: {self.hp}")
        if self.hp <= 0:
            print(f"{self.name} has been eliminated!")

    def apply_status_effect(self, effect):
        """Add a status effect to this character."""
        self.status_effects.append(effect)
        print(f"{self.name} is now affected by {effect.__class__.__name__}!")

    def is_stunned(self):
        """Return True if the character has an active stun effect."""
        return any(isinstance(e, StunEffect) for e in self.status_effects)

    def process_status_effects(self):
        """Apply each active effect, remove expired ones (calling on_expire for cleanup)."""
        for effect in self.status_effects[:]:
            effect.apply(self)
            if not effect.decrement_duration():
                effect.on_expire(self)
                self.status_effects.remove(effect)

    def start_turn(self):
        """Reset per-turn state (e.g., defend bonus) at the start of the turn."""
        if self._defending:
            self.defense = self.base_defense
            # Re-apply any active defense boost effects
            for effect in self.status_effects:
                if isinstance(effect, DefenseBoostEffect) and effect.applied:
                    self.defense += effect.defense_increase
            self._defending = False

    def set_defending(self):
        """Double defense for this turn. Resets at start of next turn."""
        self._defending = True
        self.defense *= 2


# ---------------------------------------------------------------------------
# Concrete character classes
# ---------------------------------------------------------------------------

class Gladiator(Character):
    """Melee powerhouse with high HP and a devastating Titan Smash."""

    def __init__(self):
        super().__init__("Gladiator", hp=100, attack_power=20, defense=5)
        self.speed = 10  # Slow — low dodge chance

    def special_move(self, target):
        if self.special_move_cooldown <= 0:
            damage = self.attack_power * 1.5
            print(f"{self.name} uses **Titan Smash** on {target.name} for {damage} damage!")
            target.take_damage(damage)
            self.special_move_cooldown = 2
        else:
            print(f"{self.name}'s Titan Smash is on cooldown for {self.special_move_cooldown} more turns.")


class Voidcaster(Character):
    """Mage who deals AoE damage to the entire enemy team with Arcane Blast."""

    def __init__(self):
        super().__init__("Voidcaster", hp=80, attack_power=25, defense=2)
        self.is_aoe = True

    def special_move(self, target_team):
        if self.special_move_cooldown <= 0:
            print(f"{self.name} casts **Arcane Blast**, damaging ALL opponents!")
            for enemy in target_team:
                if enemy.hp > 0:
                    damage = max(0, self.attack_power - enemy.defense)
                    enemy.take_damage(damage)
            self.special_move_cooldown = 3
        else:
            print(f"{self.name}'s Arcane Blast is on cooldown for {self.special_move_cooldown} more turns.")


class Stormstriker(Character):
    """Ranged archer with Piercing Arrow that ignores defense and may stun."""

    def __init__(self):
        super().__init__("Stormstriker", hp=90, attack_power=18, defense=4)
        self.speed = 30  # Fast — ~30% dodge chance

    def special_move(self, target):
        if self.special_move_cooldown <= 0:
            print(f"{self.name} fires **Piercing Arrow**, ignoring {target.name}'s defense!")
            target.take_damage(self.attack_power + target.defense)  # Bypasses defense

            if random.random() < 0.5:
                target.apply_status_effect(StunEffect(duration=1))
                print(f"{target.name} is stunned!")

            self.special_move_cooldown = 2
        else:
            print(f"{self.name}'s Piercing Arrow is on cooldown.")


class Nightstalker(Character):
    """Stealthy assassin with Silent Kill — deals extra damage and poisons the target."""

    def __init__(self):
        super().__init__("Nightstalker", hp=70, attack_power=30, defense=3)
        self.speed = 40  # Very fast — high dodge chance

    def special_move(self, target):
        if self.special_move_cooldown <= 0:
            if not target._defending:
                print(f"{self.name} executes **Silent Kill**, dealing double damage!")
                target.take_damage(self.attack_power * 2)
            else:
                print(f"{self.name}'s Silent Kill was reduced — target is defending.")
                target.take_damage(self.attack_power)

            target.apply_status_effect(PoisonEffect(damage_per_turn=5, duration=3))
            print(f"{target.name} is now poisoned!")
            self.special_move_cooldown = 3
        else:
            print(f"{self.name}'s Silent Kill is on cooldown.")


class Stoneguard(Character):
    """Defensive tank who uses Iron Fortress to boost defense for multiple turns."""

    def __init__(self):
        super().__init__("Stoneguard", hp=120, attack_power=15, defense=8, target_type="self")

    def special_move(self, target=None):
        if self.special_move_cooldown <= 0:
            print(f"{self.name} activates **Iron Fortress**, boosting defense for 2 turns!")
            self.apply_status_effect(DefenseBoostEffect(defense_increase=5, duration=2))
            self.special_move_cooldown = 2
        else:
            print(f"{self.name}'s Iron Fortress is on cooldown.")


class Soulmender(Character):
    """Healer who restores HP to allies with Healing Light."""

    def __init__(self):
        super().__init__("Soulmender", hp=85, attack_power=10, defense=4, target_type="ally")

    def special_move(self, target):
        if self.special_move_cooldown <= 0:
            heal_amount = 30
            target.hp = min(target.max_hp, target.hp + heal_amount)  # Capped at max HP
            actual_heal = min(heal_amount, target.max_hp - (target.hp - heal_amount))
            print(f"{self.name} uses **Healing Light**, restoring {heal_amount} HP to {target.name}! ({target.hp} HP)")
            self.special_move_cooldown = 3
        else:
            print(f"{self.name}'s Healing Light is on cooldown for {self.special_move_cooldown} more turns.")


class CharacterFactory:
    """Factory for creating character instances by class name."""

    CHARACTER_CLASSES = {
        "Gladiator": Gladiator,
        "Voidcaster": Voidcaster,
        "Stormstriker": Stormstriker,
        "Nightstalker": Nightstalker,
        "Stoneguard": Stoneguard,
        "Soulmender": Soulmender,
    }

    @staticmethod
    def create_character(character_type):
        if character_type in CharacterFactory.CHARACTER_CLASSES:
            return CharacterFactory.CHARACTER_CLASSES[character_type]()
        raise ValueError(f"Unknown character type: {character_type}")
