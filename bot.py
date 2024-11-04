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
from constants import default_pokemon_stats, bench_positions, card_offset_mapping

class PokemonBot:
    def __init__(self, app_state, log_callback):
        self.app_state = app_state
        self.log_callback = log_callback
        self.running = False
        self.template_images = load_template_images("images")
        self.card_images = load_all_cards("images/cards")
        self.deck_info = sandslash_deck

        ## COORDS
        self.zoom_card_region = (200, 360, 570, 400)
        self.turn_check_region = (50, 1560, 200, 20)
        self.center_x = 540
        self.center_y = 960
        self.card_start_x = 500
        self.card_y = 1500
        self.number_of_cards_region = (790, 1325, 60, 50)

        ## STATE
        self.hand_state = []
        self.active_pokemon = []
        self.bench_pokemon = []
        self.number_of_cards = 5

        self.image_processor = ImageProcessor(self.log_callback)
        self.battle_actions = BattleActions(self.image_processor, self.template_images, self.card_images, self.zoom_card_region, self.number_of_cards_region, self.log_callback)

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
            self.active_pokemon = []
            self.bench_pokemon = []
            screenshot = take_screenshot()

            ### GO THROUGH MENUS TO FIND A BATTLE
            if not self.image_processor.check_and_click(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen"):
                self.image_processor.check_and_click(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen")
            time.sleep(1)
            self.battle_actions.perform_search_battle_actions(screenshot, self.running, self.stop)

            ### BATTLE START
            self.image_processor.check_and_click_until_found(self.template_images["TIME_LIMIT_INDICATOR"], "Time limit indicator", self.running, self.stop)
            screenshot = take_screenshot()

            while not self.image_processor.check(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended") and (not self.image_processor.check(screenshot, self.template_images["NEXT_BUTTON"], "Next button") and not (self.image_processor.check(screenshot, self.template_images["THANKS_BUTTON"], "Thanks button")) and not (self.image_processor.check(screenshot, self.template_images["BATTLE_BUTTON"], "Battle button")) and not self.image_processor.check(screenshot, self.template_images["CROSS_BUTTON"], "Cross button") and not self.image_processor.check(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen") and not self.image_processor.check(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen")):
                ## Case got a pokemon defeated or sabrina card
                self.click_bench_pokemons()

                if self.battle_actions.check_turn(self.turn_check_region, self.running) or not self.active_pokemon:
                    time.sleep(1)
                    self.update_field_and_hand_cards()
                    self.play_turn()
                    self.try_attack()
                    self.end_turn()

                screenshot = take_screenshot()

            ### GO TO MAIN SCREEN
            time.sleep(1)
            if self.image_processor.check_and_click(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended"):
                time.sleep(1)
            if self.image_processor.check_and_click(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended"):
                time.sleep(1)
            if self.image_processor.check_and_click(screenshot, self.template_images["NEXT_BUTTON"], "Next button"):
                time.sleep(1)
            if self.image_processor.check_and_click(screenshot, self.template_images["THANKS_BUTTON"], "Thanks button"):
                time.sleep(2)
            self.image_processor.check_and_click(screenshot, self.template_images["CROSS_BUTTON"], "Cross button")


    def play_turn(self):
        if not self.running:
            return False
        self.log_callback("Start playing my turn...")
        
        ## Check playable cards (main field or bench is empty)
        for card in self.hand_state:
            if not self.running:
                return False
            
            ## Check if i can attach an energy to the main card
            self.log_callback(f"Trying to attach an energy...")
            self.add_energy_to_pokemon()

            card_offset_x = card_offset_mapping.get(self.number_of_cards, 20)
            start_x = self.card_start_x - (card['position'] * card_offset_x)
            if not self.active_pokemon and card['info']['level'] == 0 and not card['info']['item_card']:
                drag_position((start_x, self.card_y), (self.center_x, self.center_y))
                self.active_pokemon.append(card)
                time.sleep(1)
            elif len(self.bench_pokemon) < 3:
                if card['info']['level'] == 0 and not card['info']['item_card'] and card['name']:
                    for bench_position in bench_positions:
                        self.reset_view()
                        time.sleep(0.5)
                        self.log_callback(f"Playing card from position {card['position']+1} to bench {bench_position}...")
                        drag_position((start_x, self.card_y), bench_position, 1.5)

                    bench_pokemon_info = {
                        "name": card['name'].capitalize(),
                        "info": card['info'],
                        "energies": 0
                    }
                    self.bench_pokemon.append(bench_pokemon_info)

            ## Check if i can evolve the main pokemon
            if card['info'].get('evolves_from') and self.active_pokemon:
                if card['info']['evolves_from'].lower() == self.active_pokemon[0]['name'].lower():
                    card_offset_x = card_offset_mapping.get(self.number_of_cards, 20)
                    start_x = self.card_start_x - (card['position'] * card_offset_x)

                    self.log_callback(f"Evolving {self.active_pokemon[0]['name']} to {card['name']}...")
                    drag_position((start_x, self.card_y), (self.center_x, self.center_y))
                    
                    self.active_pokemon[0] = {
                        "name": card['name'],
                        "info": card['info'],
                        "energies": self.active_pokemon[0].get("energies", 0)
                    }
                    time.sleep(1)
                    self.hand_state.remove(card)
                    self.number_of_cards -= 1

            ## Check if i can play a trainer card            
            if card['info'].get('item_card'):
                card_offset_x = card_offset_mapping.get(self.number_of_cards, 20)
                start_x = self.card_start_x - (card['position'] * card_offset_x)
                
                self.log_callback(f"Playing trainer card: {card['name']}...")
                drag_position((start_x, self.card_y), (self.center_x, self.center_y))
                
                time.sleep(1)
                self.hand_state.remove(card)
                self.number_of_cards -= 1

            screenshot = take_screenshot()
            if self.image_processor.check_and_click(screenshot, self.template_images["START_BATTLE_BUTTON"], "Start battle button"):
                break
            self.reset_view()
        time.sleep(0.5)

        self.try_attack()
        ## Check if i can attach an energy to the main card
        self.log_callback(f"Trying to attach an energy...")
        self.add_energy_to_pokemon()
        if not self.running:
            return False
        ## Check if i can attack
        self.try_attack()

        if not self.running:
            return False

    def add_energy_to_pokemon(self):
        if not self.running:
            return False
        drag_position((750,1450), (self.center_x, self.center_y), 0.3)
    
    def check_cards(self, debug_images=False):
        if not self.running:
            return False
        self.log_callback(f"Start checking hand cards...")
        x = self.card_start_x
        hand_cards = []
        self.hand_state.clear()
        for i in range(self.number_of_cards):
            if not self.running:
                break
            self.reset_view()
            self.log_callback(f"Checking card {i+1} at position ({x}, {self.card_y})")

            zoomed_card_image = self.battle_actions.get_card(x, self.card_y)
            if debug_images:
                unique_id = str(uuid.uuid4())  # Convert UUID to string
                cv2.imwrite(f"{unique_id}.png",zoomed_card_image)
            card_name = self.battle_actions.identify_card(zoomed_card_image)
            hand_cards.append(card_name.capitalize() if card_name else "Unknown Card")

            card_info = self.deck_info.get(card_name, default_pokemon_stats)
            
            card_info_with_position = {
                "name": card_name,
                "info": card_info,
                "position": i
            }
            self.hand_state.append(card_info_with_position)

            x -= card_offset_mapping.get(self.number_of_cards, 20)

        hand_description = ', '.join(hand_cards)
        self.log_callback(f"Your hand contains: {hand_description}")
        #self.log_callback("Detailed hand information:")

        for card in self.hand_state:
            card_name = card["name"]
            card_info = card["info"]
            position = card["position"]
            
            # Log detailed information for each card with position
            self.log_callback(f"- Position {position}: {card_name}")

    def click_bench_pokemons(self):
        screenshot = take_screenshot()
        if  not self.running or \
            self.image_processor.check(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended") or \
            self.image_processor.check(screenshot, self.template_images["NEXT_BUTTON"], "Next button") or \
            self.image_processor.check(screenshot, self.template_images["THANKS_BUTTON"], "Thanks button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_BUTTON"], "Battle button") or \
            self.image_processor.check(screenshot, self.template_images["CROSS_BUTTON"], "Cross button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen"):
            return False
        
        self.log_callback(f"Click bench slots...")
        for bench_position in bench_positions:
            click_position(bench_position[0], bench_position[1])

    def check_field(self):
        if not self.running:
            return False
        self.log_callback(f"Checking the field...")

        zoomed_card_image = self.battle_actions.get_card(self.center_x, self.center_y, 1.5)
        main_zone_pokemon_name = self.battle_actions.identify_card(zoomed_card_image)
        if main_zone_pokemon_name:
            self.active_pokemon = []
            card_info = self.deck_info.get(main_zone_pokemon_name, default_pokemon_stats)
            card_info = {
                "name": main_zone_pokemon_name,
                "info": card_info,
                "energies": 0
            }
            self.active_pokemon.append(card_info)
        self.reset_view()
        self.bench_pokemon = []
        for index, bench_position in enumerate(bench_positions):
            zoomed_card_image = self.battle_actions.get_card(bench_position[0], bench_position[1], 1.5)
            bench_zone_pokemon_name = self.battle_actions.identify_card(zoomed_card_image)
            if bench_zone_pokemon_name:
                card_info = self.deck_info.get(bench_zone_pokemon_name, default_pokemon_stats)
                card_info = {
                    "name": bench_zone_pokemon_name,
                    "info": card_info,
                    "position": index,
                    "energies": 0
                }
                self.bench_pokemon.append(card_info)
            time.sleep(0.25)
            self.reset_view()
            time.sleep(0.25)


        if self.active_pokemon:
            active = self.active_pokemon[0]
            active_info = active["info"]
            self.log_callback(f"Active Pokémon: | {active['name']} |")
        else:
            self.log_callback("No active Pokémon in play.")

        # Log bench Pokémon details
        self.log_callback("Bench Pokémon:")
        for idx, pokemon in enumerate(self.bench_pokemon, start=1):
            info = pokemon["info"]
            self.log_callback(f"| Bench Slot {idx}: {pokemon['name']} |")
    
    def reset_view(self):
        screenshot = take_screenshot()
        if  not self.running or \
            self.image_processor.check(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended") or \
            self.image_processor.check(screenshot, self.template_images["NEXT_BUTTON"], "Next button") or \
            self.image_processor.check(screenshot, self.template_images["THANKS_BUTTON"], "Thanks button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_BUTTON"], "Battle button") or \
            self.image_processor.check(screenshot, self.template_images["CROSS_BUTTON"], "Cross button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen"):
            return False
        click_position(0,1350)
        click_position(0,1350)

    def check_n_cards(self):
        if not self.running:
            return False
        n_cards = self.battle_actions.check_number_of_cards(500, 1500)
        if n_cards:
            self.number_of_cards = int(n_cards)

    def update_field_and_hand_cards(self):
        if not self.running:
            return False
        self.reset_view()
        self.check_n_cards()
        self.reset_view()
        self.check_cards(False)
        self.reset_view()
        self.check_field()

    def end_turn(self):
        if not self.running:
            return False
        self.reset_view()
        time.sleep(0.5)
        screenshot = take_screenshot()
        self.image_processor.check_and_click(screenshot, self.template_images["END_TURN"], "End turn")
        time.sleep(0.5)
        self.image_processor.check_and_click(screenshot, self.template_images["OK"], "Ok")

    def try_attack(self):
        screenshot = take_screenshot()
        if  not self.running or \
            self.image_processor.check(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Game ended") or \
            self.image_processor.check(screenshot, self.template_images["NEXT_BUTTON"], "Next button") or \
            self.image_processor.check(screenshot, self.template_images["THANKS_BUTTON"], "Thanks button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_BUTTON"], "Battle button") or \
            self.image_processor.check(screenshot, self.template_images["CROSS_BUTTON"], "Cross button") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen") or \
            self.image_processor.check(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen"):
            return False
        self.add_energy_to_pokemon()
        time.sleep(0.25)
        self.reset_view()
        click_position(self.center_x, self.center_y)
        time.sleep(0.25)
        click_position(540, 1250)
        screenshot = take_screenshot()
        time.sleep(0.25)
        self.image_processor.check_and_click(screenshot, self.template_images["OK"], "Ok")
        self.image_processor.check_and_click(screenshot, self.template_images["OK_2"], "Ok")
        self.image_processor.check_and_click(screenshot, self.template_images["OK_3"], "Ok")
        screenshot = take_screenshot()
        time.sleep(0.25)
        self.image_processor.check_and_click(screenshot, self.template_images["OK"], "Ok")
        self.image_processor.check_and_click(screenshot, self.template_images["OK_2"], "Ok")
        self.image_processor.check_and_click(screenshot, self.template_images["OK_3"], "Ok")
        self.reset_view()