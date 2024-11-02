import time
import cv2
import threading
import numpy as np
from adb_utils import connect_to_emulator, click_position, take_screenshot, find_subimage, long_press_position, drag_position
from loaders import load_template_images, load_all_cards
import uuid
import os
from deck import sandslash_deck 
from image_utils import ImageProcessor
from battle_actions import BattleActions

class PokemonBot:
    def __init__(self, app_state, log_callback):
        self.app_state = app_state
        self.log_callback = log_callback
        self.running = False
        self.template_images = load_template_images("images")
        self.zoom_card_region = (200, 360, 570, 400)
        self.card_images = load_all_cards("images/cards")

        self.turn_check_region = (50, 1560, 200, 20)
        self.center_x = 540
        self.center_y = 960
        self.card_start_x = 500
        self.card_y = 1500
        self.card_offset_x = 60
        self.number_of_cards_region = (790, 1325, 60, 50)
        self.deck_info = sandslash_deck
        self.hand_state = []
        self.active_pokemon = []
        self.bench_pokemon = []

        self.image_processor = ImageProcessor(self.log_callback)
        self.battle_actions = BattleActions(self.image_processor, self.template_images, self.card_images, self.zoom_card_region, self.log_callback)

    def start(self):
        if not self.app_state.program_path:
            self.log_callback("Please select emulator path first.")
            return
        self.running = True
        threading.Thread(target=self.connect_and_run).start()

    def stop(self):
        self.running = False

    def connect_and_run(self):
        connect_to_emulator(self.app_state.emulator_name)
        self.log_callback("Connected to emulator")
        self.run_script()

    def run_script(self):
        while self.running:
            screenshot = take_screenshot()

            ### GO THROUGH MENUS TO FIND A BATTLE
            #if not self.image_processor.check_and_click(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen"):
            #    self.image_processor.check_and_click(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen")
            #time.sleep(1)
            #self.battle_actions.perform_search_battle_actions(self.running, self.stop)

            ### BATTLE START

            ## First turn
            self.image_processor.check_and_click_until_found(self.template_images["TIME_LIMIT_INDICATOR"], "Time limit indicator", self.running, self.stop)
            screenshot = take_screenshot()
            if not self.image_processor.check(screenshot, self.template_images["GOING_FIRST_INDICATOR"], "Going first"):
                self.image_processor.check(screenshot, self.template_images["GOING_SECOND_INDICATOR"], "Going second")
            self.battle_actions.check_rival_concede(screenshot, self.running, self.stop)
            
            number_of_cards = int(self.check_number_of_cards(500, 1500))
            self.check_cards(number_of_cards)
            screenshot = take_screenshot()
            self.battle_actions.check_rival_concede(screenshot, self.running, self.stop)
            self.play_turn()


            #if self.battle_actions.check_turn(self.turn_check_region, self.running):
            #    self.play_turn()


    def play_turn(self):
        if not self.running:
            return False
        self.log_callback("Playing turn actions...")

        # Check if there is an active Pokémon
        zoomed_card_image = self.get_card(self.center_x, self.center_y, 2)
        main_zone_pokemon_name = self.identify_card(zoomed_card_image)
            
        for card in self.hand_state:
            start_x = self.card_start_x - (card['position'] * self.card_offset_x)
            if not main_zone_pokemon_name and not self.active_pokemon and card['info']['level'] == 0 and not card['info']['item_card']:
                drag_position((start_x, self.card_y), (self.center_x, self.center_y))
                self.active_pokemon.append(card)
                # If its the first turn, just start the battle
                time.sleep(1)
                screenshot = take_screenshot()

                self.image_processor.check_and_click(screenshot, self.template_images["START_BATTLE_BUTTON"], "Start battle button")

            elif len(self.bench_pokemon) < 3:
                if card['info']['level'] == 0 and not card['info']['item_card']:
                    self.log_callback(f"Playing card from position {card['position']+1} to bench...")

                    drag_position((start_x, self.card_y), (len(self.bench_pokemon) * 200, self.center_y + 300))

                    bench_pokemon_info = {
                        "name": card['name'].capitalize(),
                        "info": card['info'],
                        "energies": 0
                    }
                    self.bench_pokemon.append(bench_pokemon_info)

        self.log_callback("Current active Pokémon and bench details:")
        self.log_active_and_bench_pokemon()

    def log_active_and_bench_pokemon(self):
        # Log active Pokémon details
        if self.active_pokemon:
            active = self.active_pokemon[0]
            active_info = active["info"]
            #self.log_callback(f"Active Pokémon: {active['name']} - Level: {active_info['level']}, Energies: {active['energies']}, "
            #                  f"Evolves from: {active_info.get('evolves_from', 'N/A')}, Can Evolve: {'Yes' if active_info.get('can_evolve') else 'No'}")
        else:
            self.log_callback("No active Pokémon in play.")

        # Log bench Pokémon details
        self.log_callback("Bench Pokémon:")
        for idx, pokemon in enumerate(self.bench_pokemon, start=1):
            info = pokemon["info"]
            self.log_callback(f"- Bench Slot {idx}: {pokemon['name']} - Level: {info['level']}, Energies: {pokemon['energies']}, "
                              f"Evolves from: {info.get('evolves_from', 'N/A')}, Can Evolve: {'Yes' if info.get('can_evolve') else 'No'}")

    def add_energy_to_pokemon(self, pokemon_name, is_active=True):
        target_list = self.active_pokemon if is_active else self.bench_pokemon
        for pokemon in target_list:
            if pokemon["name"].lower() == pokemon_name.lower():
                pokemon["energies"] += 1
                self.log_callback(f"Added 1 energy to {pokemon_name}. Total energies: {pokemon['energies']}")
                return
        self.log_callback(f"{pokemon_name} not found in {'active' if is_active else 'bench'} Pokémon.")    
    

    def check_cards(self, number_of_cards):
        x = self.card_start_x
        num_cards_to_check = number_of_cards
        hand_cards = []
        self.hand_state.clear()
        for i in range(num_cards_to_check):
            if not self.running:
                break
            self.log_callback(f"Checking card {i+1} at position ({x}, {self.card_y})")

            zoomed_card_image = self.get_card(x, self.card_y)
            #cv2.imwrite(f"{i}.png",zoomed_card_image)
            card_name = self.identify_card(zoomed_card_image)
            hand_cards.append(card_name.capitalize() if card_name else "Unknown Card")

            card_info = self.deck_info.get(card_name, {
                "level": "N/A", 
                "energies": "N/A", 
                "evolves_from": "N/A", 
                "can_evolve": "Unknown", 
                "item_card": False
            })
            
            card_info_with_position = {
                "name": card_name,
                "info": card_info,
                "position": i
            }
            self.hand_state.append(card_info_with_position)

            if num_cards_to_check == 5:
                x -= self.card_offset_x
            elif num_cards_to_check >= 4:
                x -= 80   
            else:
                x -= 40

        # Log hand details
        hand_description = ', '.join(hand_cards)
        self.log_callback(f"Your hand contains: {hand_description}")
        self.log_callback("Detailed hand information:")

        for card in self.hand_state:
            card_name = card["name"]
            card_info = card["info"]
            position = card["position"]
            
            # Extract and format attributes
            level = card_info.get("level", "N/A")
            energies = card_info.get("energies", "N/A")
            evolves_from = card_info.get("evolves_from", "N/A")
            can_evolve = "Yes" if card_info.get("can_evolve", False) else "No"
            item_card = "Item Card" if card_info.get("item_card", False) else "Not an Item Card"

            # Log detailed information for each card with position
            self.log_callback(f"- Position {position}: {card_name} - Level {level}, Energies: {energies}, "
                            f"Evolves from: {evolves_from}, Can Evolve: {can_evolve}, {item_card}")


    def get_card(self, x, y, duration=1.0):
        x_zoom_card_region, y_zoom_card_region, w, h = self.zoom_card_region
        return long_press_position(x, y, duration)[y_zoom_card_region:y_zoom_card_region+h, x_zoom_card_region:x_zoom_card_region+w]

    def identify_card(self, zoomed_card_image):
        highest_similarity = 0
        identified_card = None

        for card_name, template_image in self.card_images.items():
            base_card_name = os.path.splitext(card_name)[0]
            _, similarity = find_subimage(zoomed_card_image, template_image)
            if similarity > 0.8 and similarity > highest_similarity:
                highest_similarity = similarity
                identified_card = base_card_name

        return identified_card

    def check_number_of_cards(self, card_x, card_y):
        long_press_position(card_x, card_y, 2)
        
        number_image = self.image_processor.capture_region(self.number_of_cards_region)
        
        number = self.image_processor.extract_number_from_image(number_image)
        self.log_callback(f"Number of cards: {number}")
        
        return number