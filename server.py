# server.py

import socket
import threading
import json
import random
from typing import List, Dict, Optional

# Import your existing game logic modules
from character_1 import CharacterFactory
from actions_1 import AttackAction, DefendAction, SpecialMoveAction
from status_effects_1 import StunEffect  # <- change to status_effect_1 if that's your filename

# ----------------------------
# Minimal network protocol
# ----------------------------
# Server -> Client:
#   welcome          : { type, player_id }
#   choose_character : { type, available }
#   waiting          : { type, message }
#   game_state       : { type, state }
#   your_turn        : { type, actor, actions, targets }
#   action_result    : { type, log }
#   game_over        : { type, winner }
#   error            : { type, message }
#
# Client -> Server:
#   pick_character   : { type, choice }
#   action           : { type, action, target_index }  # action in {"attack","defend","special"}

AVAILABLE_CLASSES = [
    "Gladiator", "Voidcaster", "Stormstriker", "Nightstalker", "Stoneguard", "Soulmender"
]

class PlayerConn:
    def __init__(self, conn: socket.socket, addr: tuple, pid: int):
        self.conn = conn
        self.addr = addr
        self.pid = pid
        self.character = None  # set to Character instance
        self.team = None       # "Team 1" or "Team 2"
        self.lock = threading.Lock()

    def send(self, obj: dict):
        data = (json.dumps(obj) + "\n").encode("utf-8")
        with self.lock:
            self.conn.sendall(data)

    def recv(self) -> Optional[dict]:
        try:
            line = self._readline()
            if not line:
                return None
            return json.loads(line)
        except Exception:
            return None

    def _readline(self) -> Optional[str]:
        chunks = []
        while True:
            b = self.conn.recv(1)
            if not b:
                return None
            if b == b"\n":
                return b"".join(chunks).decode("utf-8")
            chunks.append(b)

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

# ----------------------------
# Headless battle engine (1v1)
# ----------------------------
class NetworkBattle:
    def __init__(self, players: List[PlayerConn]):
        # Two players, two teams
        self.players = players
        self.teams: Dict[str, List[PlayerConn]] = {
            "Team 1": [players[0]],
            "Team 2": [players[1]]
        }
        players[0].team = "Team 1"
        players[1].team = "Team 2"

        self.turn_order: List[PlayerConn] = players[:]
        random.shuffle(self.turn_order)

        self.actions = {
            "attack": AttackAction(),
            "defend": DefendAction(),
            "special": SpecialMoveAction(),
        }

    def everyone(self):
        return self.players

    # ---------- helpers ----------
    def alive_on_team(self, team_name: str):
        return [p for p in self.teams[team_name] if p.character and p.character.hp > 0]

    def check_team_alive(self, team_name: str) -> bool:
        return any(p.character.hp > 0 for p in self.teams[team_name] if p.character)

    def enemy_team_of(self, player: PlayerConn) -> str:
        return "Team 1" if player.team == "Team 2" else "Team 2"

    def serialize_state(self) -> dict:
        def char_info(p: PlayerConn):
            c = p.character
            if not c:
                return None
            return {
                "name": c.name,
                "hp": c.hp,
                "defense": c.defense,
                "cooldown": c.special_move_cooldown,
                "status": [f"{type(e).__name__}({e.duration})" for e in c.status_effects]
            }
        return {
            "teams": {
                t: [char_info(p) for p in plist] for t, plist in self.teams.items()
            },
            "turn_order": [p.pid for p in self.turn_order],
        }

    # ---------- battle loop ----------
    def run(self):
        # Ask both players to choose characters
        avail = AVAILABLE_CLASSES.copy()
        for p in self.players:
            p.send({"type": "choose_character", "available": avail})

        # collect choices (no duplicates)
        taken = set()
        for p in self.players:
            choice = self._wait_for_character_choice(p, avail, taken)
            taken.add(choice)
            p.character = CharacterFactory.create_character(choice)

        # initial broadcast
        self._broadcast_state("Match start!")

        # main turns
        while self.check_team_alive("Team 1") and self.check_team_alive("Team 2"):
            for p in list(self.turn_order):
                c = p.character
                if c.hp <= 0:
                    continue

                # Start-of-turn upkeep for EVERYONE
                # process status + decrement cooldown ONLY for the current actor
                c.process_status_effects()
                c.special_move_cooldown = max(0, c.special_move_cooldown - 1)

                # stun skip
                if c.has_active_effect(StunEffect):
                    self._broadcast_state(f"{c.name} is stunned and skips the turn!")
                    continue

                # build targets
                enemy_team_name = self.enemy_team_of(p)
                targets = [pp for pp in self.teams[enemy_team_name] if pp.character.hp > 0]
                ally_targets = [pp for pp in self.teams[p.team] if pp.character.hp > 0]

                # prompt current player
                p.send({
                    "type": "your_turn",
                    "actor": c.name,
                    "cooldown": c.special_move_cooldown,  # add this
                    "actions": ["attack", "defend", "special"],
                    "targets": {
                            "enemy": [self._target_label(pp) for pp in targets],
                            "ally": [self._target_label(pp) for pp in ally_targets],
                    },
                })

                # wait for action
                action_obj = self._wait_for_action(p)
                if not action_obj:
                    self._broadcast_state("A player disconnected. Ending match.")
                    return

                log = self._apply_action(p, action_obj, targets, ally_targets)
                self._broadcast_state(log)

                # check win after each action
                if not (self.check_team_alive("Team 1") and self.check_team_alive("Team 2")):
                    break

        winner = "Team 1" if self.check_team_alive("Team 1") else "Team 2"
        self._broadcast({"type": "game_over", "winner": winner})

    def _target_label(self, player_conn: PlayerConn) -> str:
        c = player_conn.character
        return f"{c.name} (HP {c.hp})"

    def _broadcast(self, obj: dict):
        for p in self.players:
            p.send(obj)

    def _broadcast_state(self, log: str):
        state = self.serialize_state()
        self._broadcast({"type": "game_state", "state": state})
        self._broadcast({"type": "action_result", "log": log})

    def _wait_for_character_choice(self, p: PlayerConn, avail: List[str], taken: set) -> str:
        p.send({"type": "welcome", "player_id": p.pid})
        while True:
            msg = p.recv()
            if not msg:
                raise RuntimeError("Client disconnected during character selection")
            if msg.get("type") == "pick_character":
                choice = msg.get("choice")
                if choice in avail and choice not in taken:
                    return choice
                else:
                    p.send({"type": "error", "message": "Invalid or already-taken character."})
            else:
                p.send({"type": "waiting", "message": "Pick a character to start."})

    def _wait_for_action(self, p: PlayerConn) -> Optional[dict]:
        while True:
            msg = p.recv()
            if msg is None:
                return None
            if msg.get("type") == "action":
                return msg

    def _apply_action(self, p: PlayerConn, action_obj: dict,
                      enemy_targets: List[PlayerConn], ally_targets: List[PlayerConn]) -> str:
        act = action_obj.get("action")
        target_index = action_obj.get("target_index")
        c = p.character

        def hp_line(before, after):
            return f"(HP {before} → {after})"

        # DEFEND
        if act == "defend":
            before_def = c.defense
            self.actions["defend"].execute(c)  # doubles defense per your implementation
            gained = c.defense - before_def
            return f"{c.name} defends, +{gained} DEF → {c.defense}."

        # ATTACK
        if act == "attack":
            target = self._safe_pick(enemy_targets, target_index)
            if not target:
                return f"{c.name} tried to attack, but no valid target."

            t = target.character
            # dodge check (mirrors your AttackAction)
            dodge_chance = t.speed / 100.0
            import random as _r
            if _r.random() < dodge_chance:
                return f"{c.name} attacks {t.name}, but {t.name} DODGES!"

            before = t.hp
            damage = max(0, c.attack_power - t.defense)
            t.hp -= damage
            after = t.hp
            if t.hp <= 0:
                return f"{c.name} attacks {t.name} for {before - after} damage {hp_line(before, after)}. {t.name} is eliminated!"
            return f"{c.name} attacks {t.name} for {before - after} damage {hp_line(before, after)}."

        # SPECIAL (universal 3-turn cooldown)
        if act == "special":
            # Block if on cooldown
            if c.special_move_cooldown > 0:
                return f"{c.name}'s special is on cooldown for {c.special_move_cooldown} more turn(s)."

            # Enemy-target specials
            if getattr(c, "target_type", "enemy") == "enemy":
                # AOE
                if getattr(c, "is_aoe", False):
                    living_chars = [pp.character for pp in enemy_targets if pp.character.hp > 0]
                    if not living_chars:
                        return f"{c.name} tried a team-wide special, but no valid targets."
                    # snapshot HPs
                    before_map = {ch.name: ch.hp for ch in living_chars}
                    c.special_move(living_chars)
                    # set universal cooldown
                    c.special_move_cooldown = 4
                    # build per-target deltas
                    parts = []
                    for ch in living_chars:
                        taken = max(0, before_map[ch.name] - ch.hp)
                        parts.append(f"{ch.name} -{taken} (HP {before_map[ch.name]} → {ch.hp})")
                    return f"{c.name} uses a team-wide special:\n  " + "\n  ".join(parts)

                # Single-target enemy special
                target = self._safe_pick(enemy_targets, target_index)
                if not target:
                    return f"{c.name} tried special, but no valid enemy target."
                t = target.character
                before = t.hp
                before_status = {type(e).__name__ for e in t.status_effects}
                c.special_move(t)
                # set universal cooldown
                c.special_move_cooldown = 3
                after = t.hp
                after_status = {type(e).__name__ for e in t.status_effects}
                delta = before - after
                status_note = ""
                new_effects = after_status - before_status
                if new_effects:
                    status_note = f" [Status applied: {', '.join(sorted(new_effects))}]"
                if delta > 0:
                    return f"{c.name} uses special on {t.name} for {delta} damage (HP {before} → {after}).{status_note}"
                else:
                    return f"{c.name} uses special on {t.name}.{status_note} (HP {before} → {after})"

            # Ally-target specials (e.g., Soulmender)
            elif c.target_type == "ally":
                target = self._safe_pick(ally_targets, target_index)
                if not target:
                    return f"{c.name} tried special, but no valid ally target."
                t = target.character
                before = t.hp
                c.special_move(t)
                # set universal cooldown
                c.special_move_cooldown = 3
                after = t.hp
                healed = max(0, after - before)
                return f"{c.name} heals {t.name} for {healed} (HP {before} → {after})."

            # Self specials (e.g., Stoneguard)
            else:
                before_def = c.defense
                before_status = {type(e).__name__ for e in c.status_effects}
                c.special_move(c)
                # set universal cooldown
                c.special_move_cooldown = 3
                gained = c.defense - before_def
                after_status = {type(e).__name__ for e in c.status_effects}
                new_effects = after_status - before_status
                status_note = f" [Status applied: {', '.join(sorted(new_effects))}]" if new_effects else ""
                if gained > 0:
                    return f"{c.name} uses a self-buff: +{gained} DEF → {c.defense}.{status_note}"
                return f"{c.name} uses a self-buff.{status_note}"

        return f"Unknown action from {c.name}."

    def _safe_pick(self, arr: List[PlayerConn], idx: Optional[int]) -> Optional[PlayerConn]:
        if idx is None:
            return None
        if 0 <= idx < len(arr):
            return arr[idx]
        return None

# ----------------------------
# Server bootstrap
# ----------------------------
class GameServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 50007):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: List[PlayerConn] = []
        self.next_pid = 1

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(2)
        print(f"Server listening on {self.host}:{self.port}. Waiting for 2 players...")

        while len(self.clients) < 2:
            conn, addr = self.sock.accept()
            player = PlayerConn(conn, addr, self.next_pid)
            self.next_pid += 1
            self.clients.append(player)
            print(f"Player {player.pid} connected from {addr}")
            player.send({"type": "welcome", "player_id": player.pid})
            if len(self.clients) < 2:
                player.send({"type": "waiting", "message": "Waiting for another player to join..."})

        # Launch the match
        try:
            battle = NetworkBattle(self.clients)
            battle.run()
        except Exception as e:
            print("Error during match:", e)
            for p in self.clients:
                try:
                    p.send({"type": "error", "message": str(e)})
                except Exception:
                    pass
        finally:
            for p in self.clients:
                p.close()
            self.sock.close()

if __name__ == "__main__":
    GameServer().start()
