import random
from character import CharacterFactory
from actions import AttackAction, DefendAction, SpecialMoveAction

# Purpose: Creates and handles the game logic and performance
class BattleManager:
    def __init__(self):
        self.players = [] # list of players
        self.teams = {"Team 1": [], "Team 2": []} # List of characters on each team
        self.turn_order = [] # list of turn order
        self.actions = {"1": AttackAction(), "2": DefendAction(), "3": SpecialMoveAction()} # Actions characters can perform

     # Purpose: Menu with player choices
    def setup_game(self):
        while True: # while number is 1,2 or 3
            print("\nChoose battle mode: ") # choose amount of players vs players
            print("1. 1v1")
            print("2. 2v2")
            print("3. 3v3")
            mode_choice = input("Enter your choice (1-3): ")

            if mode_choice in ["1", "2", "3"]:
                team_size = int(mode_choice) # creates team size based on number chosen
                break # breaks if number is no 1 2 or 3
            print("Invalid choice. Please enter 1, 2, or 3.")
        # number of teams is muliplied by 2 to get amount of players
        total_players = team_size * 2
        available_classes = ["Gladiator", "Voidcaster", "Stormstriker", "Nightstalker", "Stoneguard", "Soulmender"] # lists availibale characters


        for i in range(total_players):
            team_name = "Team 1" if i % 2 == 0 else "Team 2" # if even set to team 1 if odd set to team 2
            print(f"\n{team_name}, Player {len(self.teams[team_name]) + 1}, choose a character:") # determines the player's number in their team
            for idx, char_name in enumerate(available_classes): # generates an index (idx) and character name
                print(f"{idx+1}. {char_name}") # ensures list starts from 1 and not 0

            while True:
                choice = input("Enter the number of your character: ")
                if choice.isdigit() and 1 <= int(choice) <= len(available_classes): # ensures input is number and charcater has not been chosen
                    selected_character = available_classes.pop(int(choice)-1) # pops haracter chosen and mkaes list of characters -1
                    character = CharacterFactory.create_character(selected_character) # uses factory pattern to instantiate the selected character.
                    self.teams[team_name].append(character) # assis=gns character to the team
                    self.players.append(character) # ads character to gobal list of players
                    break
                print("Invalid choice. Try again.")

        self.turn_order = self.players[:] #Creates a copy of self.players for the turn order
        random.shuffle(self.turn_order) #Randomizes the order of player turns

    # Purpose: Main game loop
    def play_game(self):
        while self.check_team_alive("Team 1") and self.check_team_alive("Team 2"): # ensures there is atleast a character alive in both teams
            for player in self.turn_order:
                if player.hp <= 0: # if players hp is below zero, skip them
                    continue

                player.process_status_effects() # applies the ongoing status effect
                self.decrement_cooldowns() #decrement the cooldown for special move

                if player.is_stunned():
                    print(f"{player.name} is stunned and skips their turn!")
                    continue   # if player is stunned skip them

                print(f"\n{player.name}'s turn!")
                print("1. Attack  2. Defend  3. Special Move")
                choice = input("Choose an action: ") # prompts player to choose to attack, defend, or use special move

                # determines which team player should attack
                enemy_team = "Team 1" if player in self.teams["Team 2"] else "Team 2"
                target_team = self.teams[enemy_team]

                if choice == "2": # player chose defend
                    self.actions[choice].execute(player) # double defense for that turn
                elif choice == "3": # special move has been chosen
                    if player.target_type == "enemy": # if target is the enemy
                        if player.is_aoe: # checks if player is in area of effect
                            player.special_move(target_team) # special move is executed on the entire enemy team
                        else:
                            target = self.choose_target(player) # target is set to the player the attacker chose
                            player.special_move(target) # speical mvoe is executed on target
                    elif player.target_type == "ally": # if target is ally
                        target = self.choose_ally(player) # choose which character you want to perform speical move
                        player.special_move(target) # speical move is done on target
                    elif player.target_type == "self": # target is the current player
                        player.special_move(player) # perform special on themselves
                else: # player selects target
                    target = self.choose_target(player)
                    self.actions[choice].execute(player, target) # choose what action

                self.display_status()
                input("Press Enter to continue...")
        # checks if Team 1 has players alive, if not team 2 is chosen
        winning_team = "Team 1" if self.check_team_alive("Team 1") else "Team 2"
        print(f"\n{winning_team} wins the battle!")
    #Purpose: checks if players on team are alive
    def check_team_alive(self, team_name):
        return any(player.hp > 0 for player in self.teams[team_name]) # checks if any player in team has hp over 0

    #Purpose: Choose the target
    def choose_target(self, player):
        enemy_team = "Team 1" if player in self.teams["Team 2"] else "Team 2"
        available_targets = [p for p in self.teams[enemy_team] if p.hp > 0] # first determines whether the player belongs to Team 1 or Team 2, then selects the available allies from the appropriate team

        print("Choose a target:")
        for idx, target in enumerate(available_targets):
            print(f"{idx+1}. {target.name} (HP: {target.hp})")

        while True:
            choice = input("Enter target number: ")
            if choice.isdigit() and 1 <= int(choice) <= len(available_targets):
                return available_targets[int(choice)-1]
            print("Invalid choice. Try again.")

    def choose_ally(self, player):
        available_allies = [p for p in self.teams["Team 1"] if p.hp > 0] if player in self.teams["Team 1"] else [p for p in self.teams["Team 2"] if p.hp > 0]

        print("Choose an ally:")
        for idx, ally in enumerate(available_allies): # displays the characters names and hp of availble allies
            print(f"{idx+1}. {ally.name} (HP: {ally.hp})")

        while True:
            choice = input("Enter ally number: ") # choose an ally charcater
            if choice.isdigit() and 1 <= int(choice) <= len(available_allies): # if input is a number and the charcater is availble and an ally
                return available_allies[int(choice) - 1] # return the list decremented by 1
            print("Invalid choice. Try again.")

    # Purpose: Display the status of Battle
    def display_status(self):
        print("\nCurrent Battle Status:")
        for team_name, players in self.teams.items(): # Loops over each teams players and siplayes hp
            print(f"\n{team_name}:")
            for player in players:
                print(f"{player.name}: {player.hp} HP")
        # Prints the cooldown status of each player and how many turn left for it to be availble
        for player in self.players:
            print(f"{player.special_move_cooldown} turns until {player.name}'s special move is off cooldown.")
    # Purpose: Decrements players specila move cooldowns
    def decrement_cooldowns(self):
        for player in self.players:
            player.special_move_cooldown = max(0, player.special_move_cooldown - 1) # loops through players reducing cooldown by 1 ensuring it doesnt go below 0

if __name__ == "__main__":
    game = BattleManager()
    game.setup_game()
    game.play_game()
