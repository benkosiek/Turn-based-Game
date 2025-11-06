## ⚔️ Turn-Based Battle Game

A Python-based **team battle simulator** where players choose unique character classes and fight in strategic turn-based combat — now supporting **networked 1v1 battles** over sockets, with a **Tkinter GUI** interface.  
The underlying engine supports **1v1, 2v2, and 3v3** modes, status effects, and cooldown-based special abilities.

---

## 🎮 Game Overview

Players take turns choosing actions such as **Attack**, **Defend**, or a **Special Move**.  
Each character class has distinct attributes and a unique special ability that may target a single enemy, an ally, or all opponents.  

The match continues until all characters on one team are eliminated.

---

## 🧩 Key Features

- **Online multiplayer (1v1)** using Python sockets  
- **Tkinter GUI** client for interactive battles  
- **Team-based logic engine** supporting 1v1, 2v2, and 3v3 game modes  
- **6 unique character classes**, each with a signature special move  
- **Status effects**: stun, poison, and defense boost  
- **Cooldown system** for special abilities  
- **Speed-based turn order** and dodge mechanics  
- **Modular design** – core combat logic separated from GUI and networking  

---

## 🧙‍♂️ Character Classes

| Character     | Role / Description                                                                 |
|---------------|------------------------------------------------------------------------------------|
| **Gladiator** | A melee powerhouse with **Titan Smash**, dealing massive single-target damage.     |
| **Voidcaster**| A mage who uses **Arcane Blast**, an AoE attack that hits all enemies.             |
| **Stormstriker**| A ranged archer with **Piercing Arrow**, ignoring defense and possibly stunning. |
| **Nightstalker**| A stealthy assassin using **Silent Kill** to inflict poison and heavy damage.   |
| **Stoneguard** | A defensive tank who uses **Iron Fortress** to steadily raise defense.            |
| **Soulmender** | A healer who casts **Healing Light** to restore HP to allies.                     |

---

## 🪄 Actions

| Action | Description |
|--------|--------------|
| **Attack** | Basic single-target strike. |
| **Defend** | Doubles defense for one turn. |
| **Special Move** | Unique class-specific ability. May target self, ally, or all enemies. |

---

## 🧱 File Structure

| File | Purpose |
|------|----------|
| `battle_manager_1.py` | Core turn logic and battle flow |
| `character_1.py` | Character definitions and factory |
| `actions_1.py` | Attack, Defend, and Special Move implementations |
| `status_effects_1.py` | Defines and applies effects (Stun, Poison, DefenseBoost) |
| `protocol.py` | JSON-based socket protocol (safe send/receive) |
| `server.py` | Central game server that manages turns and state |
| `client_gui.py` | Tkinter client GUI for players |
| `Tests.py` | Unit tests for combat mechanics |

---

## 🖥️ Architecture Overview

