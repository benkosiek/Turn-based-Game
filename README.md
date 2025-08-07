# Turn-Based Battle Game

A Python-based turn-based team battle game where players choose unique character classes and battle in teams using attacks, defenses, and special abilities. Supports 1v1, 2v2, and 3v3 game modes.

## 🧠 Game Overview

Players take turns selecting actions like attacking, defending, or using a special move. Each character has unique stats and a special ability. The game continues until all characters on one team are eliminated.

## 🚀 Features

- Team-based battles (1v1, 2v2, or 3v3)
- 6 unique character classes with different abilities
- Cooldown management for special moves
- Status effects like stun, poison, and defense boosts
- Turn order and speed-based dodge mechanics

## 🧩 Characters

| Character     | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Gladiator     | Strong melee fighter with Titan Smash for heavy damage                     |
| Voidcaster    | Magic user with AoE (Arcane Blast) that damages all opponents              |
| Stormstriker  | Ranged attacker with Piercing Arrow that ignores defense and may stun      |
| Nightstalker  | Stealthy assassin with Silent Kill and poison damage                       |
| Stoneguard    | Tank with Iron Fortress that boosts defense over time                      |
| Soulmender    | Healer that restores HP to allies with Healing Light                       |

## ⚔️ Actions

- **Attack**: Basic attack targeting one enemy.
- **Defend**: Doubles defense for the current turn.
- **Special Move**: Unique to each character; may target self, ally, or all enemies depending on class.

## 🛠 File Structure

- `battle_manager.py`: Main game loop, team setup, action execution
- `character.py`: Character classes and factory for creating them
- `actions.py`: Defines attack, defend, and special move actions
- `status_effects.py`: Defines status effects like poison, stun, and defense boost

## ▶️ How to Run

1. Make sure you have Python 3 installed.
2. Place all `.py` files in the same directory.
3. Run the game:

```bash
python battle_manager.py
