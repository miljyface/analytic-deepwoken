# Analytic Deepwoken (DWIB Build Analytics)

**Analytic Deepwoken** is a Python-based Discord bot for the Deepwoken Institute of Building (DWIB). It provides comprehensive build analytics, lookups for equipment, talents, weapons, outfits, and mantras, along with smart functions for spellcheck and optimization.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
  - [General Commands](#general-commands)
  - [Lookup Commands](#lookup-commands)
  - [Analytics](#analytics-commands)
  - [Help Command](#help-command)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Full build analytics (Effective Health Points, Stat Evolution, Summary)
- Equipment, talent, weapon, outfit, and mantra lookups with fuzzy matching
- Clean, modular codebase for easy extension

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/miljyface/analytic-deepwoken.git
   cd analytic-deepwoken
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\\Scripts\\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. Create a `.env` file in the project root with your Discord bot token:
   ```dotenv
    BOT_TOKEN = TOKEN HERE
    DATABASE_KEY= ACCESS KEY HERE
    TOKENIZERS_PARALLELISM = false
    DATABASE_URL = https://idyjvmmldtdvpklkzrgr.supabase.co
   ```
2. Start the bot:
   ```bash
   python bot.py
   ```

---

## Commands

### General Commands

| Command        | Description                                  |
| -------------- | -------------------------------------------- |
| DNE            | DNE                                          |

### Lookup Commands

| Command                     | Description                                  |
| --------------------------- | -------------------------------------------- |
| `.equipment <name>`   | Lookup Equipment details                     |
| `.talent <name>`      | Lookup Talent details                        |
| `.weapon <name>`      | Lookup Weapon details                        |
| `.outfit <name>`      | Lookup Outfit details                        |
| `.mantra <name>`      | Lookup Mantra details                        |

### Analytics Commands

| Reply to Build Link         | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| `ehp`.                      | Calculates Effective Health Points of a full Phys and HP kit |
| `stats`.                    | Displays the Stat Evolution diagram for visualisation of optimisation |

Please refer to [Intepretations](#interpretations) for a general guide on how to read the analytics.

---

## Interpretations
![what you'd see when you analyse stats](evo_plot.webp)
This graph is separated into three segments, **Attunement**, **Weapon**, and **Base**. Each segment contains non-zero stat categories, with three stems to each category, the magnitude of the stems denoting the investment. 

- **Red**: Pre-Shrine
- **Gray**: Immediately after Shrine of Order
- **Black**: Post-Shrine

For stats that are not required reinvestments (Fortitude, Weapons, Attunements), a blue bar will be drawn between the **Gray** apex and the **Black** apex, denoting the **Reinvestment Interval**. For key stats, this interval will be gray instead.

The total blue on the graph is the amount of points that you have returned after using Shrine of Order. Builds with more blue usually means an unoptimal build, but this is not concrete.

---

## Examples

- **Lookup Mantra (proper)**:  `.weapon Champion's Sword`
- **Lookup Weapon (substring search)**:  `.weapon n's swor`
- **Lookup Weapon (spellcheck)**: `.weapon gale hb`
- **Analyze Build EHP**: `(replying to build link) ehp`
---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for enhancements, bug fixes, or new features.

---

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute.
