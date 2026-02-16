import random
from character import CharacterFactory
from actions import AttackAction, DefendAction, SpecialMoveAction


class BattleManager:
    """Manages game setup, turn order, and the main battle loop (local multiplayer)."""

    def __init__(self):
        self.players = []
        self.teams = {"Team 1": [], "Team 2": []}
        self.turn_order = []
        self.actions = {
            "1": AttackAction(),
            "2": DefendAction(),
            "3": SpecialMoveAction(),
        }

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup_game(self):
        """Prompt players to choose battle mode and characters."""
        while True:
            print("\nChoose battle mode:")
            print("1. 1v1")
            print("2. 2v2")
            print("3. 3v3")
            mode_choice = input("Enter your choice (1-3): ")

            if mode_choice in ["1", "2", "3"]:
                team_size = int(mode_choice)
                break
            print("Invalid choice. Please enter 1, 2, or 3.")

        total_players = team_size * 2
        available_classes = [
            "Gladiator", "Voidcaster", "Stormstriker",
            "Nightstalker", "Stoneguard", "Soulmender",
        ]

        for i in range(total_players):
            team_name = "Team 1" if i % 2 == 0 else "Team 2"
            player_num = len(self.teams[team_name]) + 1
            print(f"\n{team_name}, Player {player_num}, choose a character:")

            for idx, char_name in enumerate(available_classes):
                print(f"{idx + 1}. {char_name}")

            while True:
                choice = input("Enter the number of your character: ")
                if choice.isdigit() and 1 <= int(choice) <= len(available_classes):
                    selected_name = available_classes.pop(int(choice) - 1)
                    character = CharacterFactory.create_character(selected_name)
                    self.teams[team_name].append(character)
                    self.players.append(character)
                    break
                print("Invalid choice. Try again.")

        self.turn_order = self.players[:]
        random.shuffle(self.turn_order)

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------

    def play_game(self):
        """Run turns until one team is fully eliminated."""
        while self.check_team_alive("Team 1") and self.check_team_alive("Team 2"):
            for player in self.turn_order:
                if player.hp <= 0:
                    continue

                # Start-of-turn: reset defend bonus, apply status effects, tick cooldown
                player.start_turn()
                player.process_status_effects()
                player.special_move_cooldown = max(0, player.special_move_cooldown - 1)

                if player.is_stunned():
                    print(f"\n{player.name} is stunned and skips their turn!")
                    continue

                print(f"\n{player.name}'s turn!")
                enemy_team_name = "Team 1" if player in self.teams["Team 2"] else "Team 2"
                target_team = self.teams[enemy_team_name]

                # Prompt for action (with validation)
                choice = self._get_action_choice(player)

                if choice == "2":
                    self.actions[choice].execute(player)
                elif choice == "3":
                    self._handle_special_move(player, target_team)
                else:  # Attack
                    target = self.choose_target(player)
                    self.actions["1"].execute(player, target)

                self.display_status()
                input("Press Enter to continue...")

                if not (self.check_team_alive("Team 1") and self.check_team_alive("Team 2")):
                    break

        winning_team = "Team 1" if self.check_team_alive("Team 1") else "Team 2"
        print(f"\n{winning_team} wins the battle!")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_action_choice(self, player):
        """Prompt for a valid action choice."""
        while True:
            print("1. Attack  2. Defend  3. Special Move")
            choice = input("Choose an action: ")
            if choice in ["1", "2", "3"]:
                if choice == "3" and player.special_move_cooldown > 0:
                    print(f"Special move is on cooldown for {player.special_move_cooldown} more turn(s). Choose another action.")
                    continue
                return choice
            print("Invalid choice. Enter 1, 2, or 3.")

    def _handle_special_move(self, player, target_team):
        """Route the special move to the correct target(s)."""
        if player.target_type == "enemy":
            if player.is_aoe:
                player.special_move(target_team)
            else:
                target = self.choose_target(player)
                player.special_move(target)
        elif player.target_type == "ally":
            target = self.choose_ally(player)
            player.special_move(target)
        elif player.target_type == "self":
            player.special_move(player)

    def check_team_alive(self, team_name):
        """Return True if at least one player on the team is alive."""
        return any(p.hp > 0 for p in self.teams[team_name])

    def choose_target(self, player):
        """Let the player pick a living enemy target."""
        enemy_team = "Team 1" if player in self.teams["Team 2"] else "Team 2"
        available = [p for p in self.teams[enemy_team] if p.hp > 0]

        print("Choose a target:")
        for idx, target in enumerate(available):
            print(f"{idx + 1}. {target.name} (HP: {target.hp})")

        while True:
            choice = input("Enter target number: ")
            if choice.isdigit() and 1 <= int(choice) <= len(available):
                return available[int(choice) - 1]
            print("Invalid choice. Try again.")

    def choose_ally(self, player):
        """Let the player pick a living ally target."""
        team_name = "Team 1" if player in self.teams["Team 1"] else "Team 2"
        available = [p for p in self.teams[team_name] if p.hp > 0]

        print("Choose an ally:")
        for idx, ally in enumerate(available):
            print(f"{idx + 1}. {ally.name} (HP: {ally.hp})")

        while True:
            choice = input("Enter ally number: ")
            if choice.isdigit() and 1 <= int(choice) <= len(available):
                return available[int(choice) - 1]
            print("Invalid choice. Try again.")

    def display_status(self):
        """Print HP and cooldown status for all players."""
        print("\n--- Battle Status ---")
        for team_name, players in self.teams.items():
            print(f"\n{team_name}:")
            for p in players:
                status = "ELIMINATED" if p.hp <= 0 else f"{p.hp} HP"
                effects = ", ".join(type(e).__name__ for e in p.status_effects) or "None"
                print(f"  {p.name}: {status} | DEF: {p.defense} | Effects: {effects}")

        print()
        for p in self.players:
            if p.hp > 0 and p.special_move_cooldown > 0:
                print(f"  {p.name}'s special move: {p.special_move_cooldown} turn(s) until ready.")


if __name__ == "__main__":
    game = BattleManager()
    game.setup_game()
    game.play_game()
