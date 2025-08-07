import random
from abc import ABC, abstractmethod
from status_effects import StunEffect, PoisonEffect, DefenseBoostEffect

# Abstract Character Class
# Purpose: Defines Character parameters
class Character(ABC):
    def __init__(self, name, hp, attack_power, defense, speed = 15, is_aoe=False, target_type="enemy"):
        self.name = name  # name of character
        self.hp = hp # amount of health points a character has
        self.attack_power = attack_power # how much damage the character does
        self.defense = defense # how much defense the character has
        self.special_move_cooldown = 0 # cooldown for special move (initally set to 0)
        self.status_effects = [] # effect on character such as poison or stun
        self.is_aoe = is_aoe # checks if character is in area of effect, used for voidcaster
        self.target_type = target_type # type of target
        self.speed = speed # how fast a character is, used for dodgin purposes

    # abstract method
    # each charcater must implement their own special move
    @abstractmethod
    def special_move(self, target):
        pass

    # Purpose: Calculates how much damage charcater takes
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense) # damage (previously defined) max(0, attacker.attack_power - target.defense) subreacted from selected characters defense
        self.hp -= actual_damage # sets the characters hp after taking damage
        print(f"{self.name} takes {actual_damage} damage! Remaining HP: {self.hp}")
        # if hp is less than 0, character was elimnated
        if self.hp <= 0:
            print(f"{self.name} has been eliminated!")
    # Purpose: Applies an effect on character
    def apply_status_effect(self, effect):
        self.status_effects.append(effect) # appened the effect
        print(f"{self.name} is now affected by {effect.__class__.__name__}!")

    def is_stunned(self):
        for effect in self.status_effects:
            if isinstance(effect, StunEffect):
                return True
        return False
    # Purpose: Process the effect
    def process_status_effects(self):
        for effect in self.status_effects[:]:
            effect.apply(self) # applies the effect in status effect list
            if not effect.decrement_duration():
                self.status_effects.remove(effect) # rremove effect after decremantation

# Purpose: Creates a Gladiator character
# Implements abstract character class
class Gladiator(Character):
    def __init__(self):
        super().__init__("Gladiator", hp=100, attack_power=20, defense=5) # sets unqiue variables
        self.speed = 10 # slow low chance of dodge
    # Gladiators special move
    def special_move(self, target):
        if self.special_move_cooldown <= 0: # checks if not in cooldown
            damage = self.attack_power * 1.5 # increases Gladiators attack damage by 1.5
            print(f"{self.name} uses **Titan Smash** on {target.name} for {damage} damage!")
            target.take_damage(damage) # selected target to take damage
            self.special_move_cooldown = 2 #set special move cooldown to 2
        else: # if speicial move is on cooldonw (>0)
            print(f"{self.name}'s Titan Smash is on cooldown for {self.special_move_cooldown} more turns.")

# Purpose: Creates a Voidcaster character
# Implemented abstract Character class
class Voidcaster(Character):
    def __init__(self):
        super().__init__("Voidcaster", hp=80, attack_power=25, defense=2) # sets unqiue varibales
        self.is_aoe = True  # is in area of affect

    # Purpose: Voidcaster special move
    def special_move(self, target_team): # called on mulitple targets
        if self.special_move_cooldown <= 0: # checks if eligable to execute speicla move
            print(f"{self.name} casts **Arcane Blast**, damaging ALL opponents!")

            for enemy in target_team: # speical move affects all targtes in target_team
                if enemy.hp > 0:
                    damage = max(0, self.attack_power - enemy.defense)
                    enemy.take_damage(damage)

            self.special_move_cooldown = 3 # set cooldwon back to 3
        else: # special move is still on cooldown
            print(f"{self.name}'s Arcane Blast is on cooldown for {self.special_move_cooldown} more turns.")

# Creates a Stormstriker Character
# Implemented abstract Character class
class Stormstriker(Character):
    def __init__(self):
        super().__init__("Stormstriker", hp=90, attack_power=18, defense=4)
        self.speed = 30 # Character is quick and able to dodge around 30% of time

    #Called on selected target
    def special_move(self, target):
        if self.special_move_cooldown <= 0: # checks if able to perform speical move
            print(f"{self.name} fires **Piercing Arrow**, ignoring {target.name}'s defense!")
            target.take_damage(self.attack_power + target.defense) # target takes the character Stormstrikers damage and their defense added together


            if random.random() < 0.5:
                target.apply_status_effect(StunEffect(duration=1))  # stuns target for a tunr
                print(f"{target.name} is stunned!")

            self.special_move_cooldown = 2 # sets cooldown to 2
        else: # if cooldown is greater than 0
            print(f"{self.name}'s Piercing Arrow is on cooldown.")

# Creates a Nighstalker Character
# implements the abstract character class
class Nightstalker(Character):
    def __init__(self):
        super().__init__("Nightstalker", hp=70, attack_power=30, defense=3) # unique character varuables
        self.speed = 40 # fast and able to dodge

    # Purpose: Nightstalkers special move
    def special_move(self, target):
        if self.special_move_cooldown <= 0: # checks if not on cooldown
            if target.defense == 0: # if target is not defening
                print(f"{self.name} executes **Silent Kill**, dealing double damage!")
                target.take_damage(self.attack_power * 2) # increases attack power of Nightstalker by 2
            else: # if target chose to defend
                print(f"{self.name}'s Silent Kill was reduced due to defense.")
                target.take_damage(self.attack_power) # does normal Nightstalker damage

            target.apply_status_effect(PoisonEffect(damage_per_turn=5, duration=3)) # posions target for 5 damage for 3 ticks
            print(f"{target.name} is now poisoned!")

            self.special_move_cooldown = 3 # Rest cooldown to 3
        else: # special move was on cooldown
            print(f"{self.name}'s Silent Kill is on cooldown.")

# Creates Stoneguard character
# Implements the abstract Character Class
class Stoneguard(Character):
    def __init__(self):
        super().__init__("Stoneguard", hp=120, attack_power=15, defense=8, target_type="self")

    # Does not perform on a target but only on self
    def special_move(self, target=None):
        if self.special_move_cooldown <= 0: # makes sure it is not on cooldown
            print(f"{self.name} activates **Iron Fortress**, reducing all damage for 2 turns!")
            self.apply_status_effect(DefenseBoostEffect(defense_increase=5, duration=2)) # applies defense boost
            self.special_move_cooldown = 2 # resets cooldown
        else: # if special move was on cooldown
            print(f"{self.name}'s Iron Fortress is on cooldown.")

# Creates a Soulmender character
# Implements the abstract Character Class
class Soulmender(Character):
    def __init__(self):
        super().__init__("Soulmender", hp=85, attack_power=10, defense=4, target_type="ally")
    # Purpose: Soulmenders speical move
    # perfomrs on target
    def special_move(self, target):
        if self.special_move_cooldown <= 0: # checks if specialmove is not on cooldown
            heal_amount = 30 # amount of healing special move does
            target.hp += heal_amount # selected target gets their health increased by 30
            print(f"{self.name} uses **Healing Light**, restoring {heal_amount} HP to {target.name}!")
            self.special_move_cooldown = 3 # resets cooldown to 3
        else:
            print(f"{self.name}'s Healing Light is on cooldown for {self.special_move_cooldown} more turns.")

# Purpose: Creayes instances of different character types based on a given name
class CharacterFactory:
    
    @staticmethod
    def create_character(character_type):
        # Dictionary mapping character type names to their respective class constructors.
        character_classes = {
            "Gladiator": Gladiator,
            "Voidcaster": Voidcaster,
            "Stormstriker": Stormstriker,
            "Nightstalker": Nightstalker,
            "Stoneguard": Stoneguard,
            "Soulmender": Soulmender
        }
        # Check if the character type exists in the dictionary
        if character_type in character_classes:
            return character_classes[character_type]()
        else:
            raise ValueError(f"Unknown character type: {character_type}")
