## ⚔️ Turn-Based Battle Game

A Python-based **team battle simulator** where players choose unique character classes and fight in strategic turn-based combat — supporting **networked 1v1 battles** over TCP sockets with a **Tkinter GUI** client.  
The underlying engine also supports **2v2 and 3v3** local modes, status effects, and cooldown-based special abilities.

---

## 🎮 Game Overview

Players take turns choosing actions: **Attack**, **Defend**, or a **Special Move**.  
Each character class has distinct attributes and a unique special ability that may target a single enemy, an ally, all opponents, or the player themselves.  

The match continues until all characters on one team are eliminated.

---

## 🧩 Key Features

- **Online multiplayer (1v1)** using Python TCP sockets with JSON protocol  
- **Tkinter GUI** client for interactive battles  
- **Local multiplayer engine** supporting 1v1, 2v2, and 3v3 modes  
- **6 unique character classes**, each with a signature special move  
- **Status effects**: Stun, Poison, and Defense Boost (with proper expiry cleanup)  
- **Cooldown system** for special abilities  
- **Speed-based dodge mechanics**  
- **Design patterns**: Abstract Factory, Strategy, Template Method  

---

## 🧙‍♂️ Character Classes

| Character       | HP  | ATK | DEF | Speed | Special Move     | Description                                                  |
|-----------------|-----|-----|-----|-------|------------------|--------------------------------------------------------------|
| **Gladiator**   | 100 | 20  | 5   | 10    | Titan Smash      | Deals 1.5× damage to a single target                        |
| **Voidcaster**  | 80  | 25  | 2   | 15    | Arcane Blast      | AoE — hits all enemies                                      |
| **Stormstriker**| 90  | 18  | 4   | 30    | Piercing Arrow    | Ignores defense; 50% chance to stun                         |
| **Nightstalker**| 70  | 30  | 3   | 40    | Silent Kill       | Double damage if target isn't defending; applies poison      |
| **Stoneguard**  | 120 | 15  | 8   | 15    | Iron Fortress     | Grants +5 defense for 2 turns (self-target)                 |
| **Soulmender**  | 85  | 10  | 4   | 15    | Healing Light     | Restores 30 HP to an ally (capped at max HP)                |

---

## 🪄 Actions

| Action           | Description                                                        |
|------------------|--------------------------------------------------------------------|
| **Attack**       | Basic single-target strike. Damage = ATK − target DEF (min 0).    |
| **Defend**       | Doubles defense for the current turn, then resets.                 |
| **Special Move** | Unique class-specific ability with a cooldown between uses.        |

---

## 🧱 File Structure

| File                | Purpose                                           |
|---------------------|---------------------------------------------------|
| `server.py`         | TCP game server — manages connections and turns    |
| `client_gui.py`     | Tkinter GUI client for players                     |
| `battle_manager.py` | Local multiplayer battle loop and game logic        |
| `character.py`      | Character class definitions and factory             |
| `actions.py`        | Attack, Defend, and Special Move implementations    |
| `status_effects.py` | Status effect classes (Stun, Poison, DefenseBoost)  |

---

## ▶️ How To Run

**Start the server:**
```bash
python server.py
```

**Connect clients** (run in separate terminals):
```bash
python client_gui.py
```

**Play locally** (no server needed — terminal-based):
```bash
python battle_manager.py
```

---

## 🛠️ Technical Highlights

- **OOP Architecture**: Abstract base classes with inheritance and polymorphism for characters, actions, and status effects  
- **Factory Pattern**: `CharacterFactory` creates character instances by name  
- **Strategy Pattern**: Interchangeable `Action` classes (`AttackAction`, `DefendAction`, `SpecialMoveAction`)  
- **Client–Server Networking**: JSON-over-TCP protocol with newline delimiters, threaded I/O  
- **State Management**: Defense buffs properly reset per turn; status effects clean up on expiry
