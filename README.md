<h1 align="center">
  <br>
  <a href="https://tcgpocket.Pokemon.com/es-es/"><img src="https://github.com/user-attachments/assets/141d27c3-d965-4bb9-ab02-2d61af431aef" alt="Markdownify" width="200"></a>
  <br>
  Pokemon Pocket Bot ⚔️
  <br>
  <h4 align="center">A computer vision bot made with <a href="https://opencv.org/" target="_blank">OpenCV</a> and <a href="https://developer.android.com/studio/command-line/adb" target="_blank">ADB</a>.</h4>

<p align="center">
  <a href="www.python.org">
    <img src="https://badgen.net/badge/python/3.12/pink?icon=terminal"
         alt="Python">
  </a>
  <a href="https://img.shields.io/github/repo-size/AdriaGual/pokemon-pocket-bot">
    <img src="https://img.shields.io/github/repo-size/AdriaGual/pokemon-pocket-bot">
  </a>
  <a href="https://pypi.org/">
      <img src="https://img.shields.io/pypi/v/nine">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://badgen.net/pypi/license/pip">
  </a>
</p>
</h1>

## Description:

The Pokemon Pocket Bot is an automation tool designed to streamline gameplay within the "Pokemon Pocket" game. Tailored specifically for LDPlayer, an Android emulator, this bot simplifies repetitive tasks by automating gameplay actions, allowing users to focus on strategic decisions and progression.

![Animation](https://github.com/user-attachments/assets/366c8543-0558-4e4b-99dc-a1f4ed3476ef)

## Usage:

- **1. Start LDPlayerEmulator**
- **2. Enable ADB connection** Open Local connection
- **3. Choose the resolution to be 1600x900 (dpi 240)**
- **4. Install the requirements**: pip install -r requirements.txt
- **5. Start the bot**: python app.py
- **6. Start Pokemon Pocket** (the game must be in english)
- **7. Choose the path to the emulator** You have to choose the main folder of the emulator (in the LDPlayer case would be LDPlayer/LDPlayer9)
- **8. Start botting** You can choose between two modes, Auto Concede to farm fast matches and Start Bot, still WIP.

## LDPlayer Settings:
<a href="https://tcgpocket.Pokemon.com/es-es/"><img src="https://github.com/user-attachments/assets/103033d6-10c2-4d23-bc85-5be2b5b64ce6" alt="Markdownify" width="600"></a>
<br>
<a href="https://tcgpocket.Pokemon.com/es-es/"><img src="https://github.com/user-attachments/assets/be415ce5-bd80-4276-b4f9-49be8f697ad3" alt="Markdownify" width="600"></a>

## Deck Configuration

One of the best features of this bot is its flexibility to use any custom deck—no specific cards are required! You can modify the deck settings by editing `deck.py`. Each card in the deck is defined in a dictionary format, with various attributes describing its properties. Here’s how each attribute works:

### Card Format

Each card entry in `deck.py` has the following structure:

```python
"rattata": {
    "level": 0,
    "energies": 1,
    "evolves_from": None,
    "can_evolve": True,
    "item_card": False
},
```

#### Attribute Explanations:

- **`level`**: This indicates the evolution stage of the Pokemon:
  - `0`: Basic Pokemon, the starting stage.
  - `1`: Stage 1 Pokemon, evolves from a basic Pokemon.
  - `2`: Stage 2 Pokemon, evolves from a Stage 1 Pokemon.

- **`energies`**: The number of energies needed for this Pokemon to perform an attack. Set this to the minimum number of energies typically required to use its main move.

- **`evolves_from`**: If this Pokemon evolves from another, set this to the exact name of its pre-evolution (e.g., `"evolves_from": "rattata"` for Raticate). For basic Pokemon, set this to `None`.

- **`can_evolve`**: A boolean value (`True` or `False`) indicating if this card is capable of evolving into a higher stage. Set this to `True` if there is a corresponding evolution in your deck.

- **`item_card`**: Set to `True` if this is a Trainer card. Trainer cards are treated as single-use items in the bot's logic and can be played directly onto the field.

By modifying the entries in `deck.py` to match your preferred cards, you can fully customize the bot’s deck to fit your strategy. Just be sure each Pokemon and Trainer card entry is formatted correctly to avoid any errors!

### Adding New Cards

If you want to use cards that aren’t currently available in the `images/cards` folder, you’ll need to add them yourself by capturing a screenshot. You can use the `screenshot` function from the bot app to take a capture at 100% resolution. After capturing, crop the image precisely to the card area and save it in the `images/cards` folder with the corresponding name (check the ones already created). This will allow the bot to recognize and use these new cards in your custom deck.

## Key Features:

- **Emulator Path Selection:** Users can easily specify the path to their LDPlayer installation within the bot's interface, facilitating seamless integration with the emulator.
  
- **Play Random Matches:** With automated matches functionality, the bot plays random matches to farm store tickets and 15 exp.

- **Concede Random Matches:** With automated matches functionality, the bot concedes random matches to farm store tickets.

## Benefits:

- **Efficiency:** By automating repetitive tasks such as lamp rolling and dungeon exploration, the bot significantly reduces the time and effort required for gameplay, allowing players to achieve their goals more efficiently.
  
- **Optimization:** Through intelligent equipment management and strategic decision-making, the bot maximizes the effectiveness of in-game resources, enhancing the player's overall gaming experience.
  
- **Convenience:** The user-friendly interface and seamless integration with LDPlayer make the bot easy to set up and operate, providing players with a convenient solution for enhancing their gameplay experience.

## Roadmap

These are the key milestones for the current and future versions of the bot:

- [x] Search for the time limit icon
- [x] Determine if it’s your turn or the enemy turn
- [x] Analyze hand cards
- [x] Analyze cards on the field
- [x] Play basic Pokemon on the main field
- [x] Play basic Pokemon on the bench fields
- [x] Attach energy to the main Pokemon
- [x] Evolve the main Pokemon
- [x] Use Trainer cards
- [x] Attack with the main Pokemon
- [x] End turn
- [x] Run in a continuous 24/7 loop
- [ ] Track energy count for each Pokemon
- [ ] Enable evolution of bench Pokemon
- [ ] Inspect the enemy’s main Pokemon
- [ ] Check health of the enemy’s main Pokemon
- [ ] Track and calculate attack power for each Pokemon
- [ ] Monitor health of the main Pokemon
- [ ] Implement a priority queue to select the optimal Pokemon for play
- [ ] Read decks from txt files
- [ ] Support multiple languages 

This checklist can be updated over time as more features are added and improved, ensuring steady progress toward full automation and strategic gameplay.

## Target Audience:

- **Gamers:** Pokemon Pocket players seeking to streamline gameplay and optimize resource management.
  
- **LDPlayer Users:** Users of the LDPlayer Android emulator looking to enhance their gaming experience through automation.

Overall, the Pokemon Pocket Bot offers a powerful yet user-friendly solution for automating gameplay tasks within the Pokemon Pocket game, providing players with greater efficiency, optimization, and convenience in their gaming journey.
