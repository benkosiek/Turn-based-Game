import random
from abc import ABC, abstractmethod

# Abstract Action Class
# sub classes must implement the execute method
class Action(ABC):
    @abstractmethod
    def execute(self, player, target=None): # intially set to None
        pass

# Purpose: Performs an attack on target
#
class AttackAction(Action):
    def execute(self, attacker, target): #execute class from Action abtract class is called on attacker and target
        if target is None: # if these is no target selected by player return message
            print("No target selected!")
            return
        # Chance of target doding attack
        # targets speed divided by 100 to get percentage chnage of attack
        # chooses random number, if less than dodge chance returns player dodged
        dodge_chance = target.speed / 100
        if random.random() < dodge_chance:
            print(f"{target.name} dodges the attack!")
            return
        # if target does not dodge damage is done
        # target health is decremented by the attacker power subtractde by target defense
        else:
            damage = max(0, attacker.attack_power - target.defense)
            target.hp -= damage
            print(f"{attacker.name} attacks {target.name} for {damage} damage!")
            # determines if target is eliminated
            if target.hp <= 0:
                print(f"{target.name} has been eliminated!")

# Purpose: Increases player defense
class DefendAction(Action):
    def execute(self, player): #execute from abstract Action class is called on current player
        original_defense = player.defense
        player.defense *= 2 # multipy players base defense by 2
        print(f"{player.name} defends, increasing defense from {original_defense} to {player.defense}!")

# Purpose: Perform player special move
class SpecialMoveAction(Action):
    def execute(self, player, target): # execute from abstract Action class is called on player and target
        if player.special_move_cooldown == 0: # checks if players cooldown is 0
            player.special_move(target) # perform special move on target (defender) if cooldown is 0
        else: # means special move was recenlty used and still in cooldown
            print(f"{player.name}'s special move is on cooldown for {player.special_move_cooldown} more turns.")
