import time
import cv2
import threading
import numpy as np
from adb_utils import connect_to_emulator, click_position, take_screenshot, find_subimage, long_press_position
from loaders import load_template_images, load_all_cards
import uuid
import os
import easyocr


class PokemonBot:
    def __init__(self, app_state, log_callback):
        self.app_state = app_state
        self.log_callback = log_callback
        self.running = False
        self.template_images = load_template_images("images")
        
        self.turn_check_region = (50, 1560, 200, 20)
        self.card_start_x = 500
        self.card_y = 1500
        self.card_offset_x = 60
        self.zoom_card_region = (200, 360, 570, 400)
        self.card_images = load_all_cards("images/cards")
        self.number_of_cards_region = (790, 1325, 60, 50)
        self.reader = easyocr.Reader(['en'])

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
            #screenshot = take_screenshot()

            ### GO THROUGH MENUS TO FIND A BATTLE
            #if not self.check_and_click(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen"):
            #    self.check_and_click(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen")
            #time.sleep(1)
            #self.perform_search_battle_actions()

            ### BATTLE START
            #self.check_and_click_until_found(self.template_images["TIME_LIMIT_INDICATOR"], "Time limit indicator")
            #screenshot = take_screenshot()
            #if not self.check(screenshot, self.template_images["GOING_FIRST_INDICATOR"], "Going first"):
            #    self.check(screenshot, self.template_images["GOING_SECOND_INDICATOR"], "Going second")
            
            number_of_cards = int(self.check_number_of_cards(500, 1500))
            self.check_cards(number_of_cards)

            if self.check_turn():
                self.play_turn()



    def perform_search_battle_actions(self):
        for key in [
            "VERSUS_SCREEN",
            "RANDOM_MATCH_SCREEN",
            "BATTLE_BUTTON",
        ]:
            if not self.check_and_click_until_found(self.template_images[key], f"{key.replace('_', ' ').title()}"):
                break

    def play_turn(self):
        if not self.running:
            return False
        # Logic to select and play cards goes here
        self.log_callback("Playing turn actions...")
        # Example: self.check_and_click_until_found(self.template_images["SOME_CARD"], "Card X")

    def check_turn(self): 
        if not self.running:
            return False
        screenshot1 = self.capture_region(self.turn_check_region)
        time.sleep(1)
        screenshot2 = self.capture_region(self.turn_check_region)

        similarity = self.calculate_similarity(screenshot1, screenshot2)
        if similarity < 0.95:
            self.log_callback("It's your turn! Taking action...")
        else:
            self.log_callback("Waiting for opponent's turn...")

        return similarity < 0.95
    

    def check_cards(self, number_of_cards):
        x = self.card_start_x
        num_cards_to_check = number_of_cards
        hand_cards = []

        for i in range(num_cards_to_check):
            if not self.running:
                break
            self.log_callback(f"Checking card {i+1} at position ({x}, {self.card_y})")

            zoomed_card_image = self.get_card(x, self.card_y)
            unique_id = str(uuid.uuid4())
            cv2.imwrite(f"debug_screenshot{unique_id}.png", zoomed_card_image)
            card_name = self.identify_card(zoomed_card_image)
            hand_cards.append(card_name if card_name else "Unknown Card")

            if num_cards_to_check <= 5:
                x -= self.card_offset_x
            else:
                x -= 40    
        hand_description = ', '.join(hand_cards)
        self.log_callback(f"Your hand contains:")
        self.log_callback(f"{hand_description}")

    def get_card(self, x, y, duration=1.0):
        x_zoom_card_region, y_zoom_card_region, w, h = self.zoom_card_region
        return long_press_position(x, y)[y_zoom_card_region:y_zoom_card_region+h, x_zoom_card_region:x_zoom_card_region+w]

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
        long_press_position(card_x, card_y, 4)
        
        number_image = self.capture_region(self.number_of_cards_region)
        
        number = self.extract_number_from_image(number_image)
        self.log_callback(f"Number of cards: {number}")
        
        return number

    def capture_region(self, region):
        x, y, w, h = region
        screenshot = take_screenshot()
        return screenshot[y:y+h, x:x+w]

    def calculate_similarity(self, img1, img2):
        """Calculate similarity between two images using structural similarity index (SSIM)."""
        if img1.shape != img2.shape:
            return 0
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        return np.mean(img1_gray == img2_gray)

    def extract_number_from_image(self, image):
        # Convert to grayscale to improve OCR accuracy
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use EasyOCR to read text from the cropped image
        result = self.reader.readtext(grayscale_image, detail=0)

        # Filter out non-numeric results, assuming the region contains a number only
        numbers = [text for text in result if text.isdigit()]
        
        if numbers:
            return numbers[0]  # Return the first recognized number if found
        else:
            return None

    def perform_concede_actions(self):
        for key in [
            "MATCH_MENU_BUTTON",
            "CONCEDE_BUTTON",
            "CONCEDE_ACCEPT_BUTTON",
            "TAP_TO_PROCEED_BUTTON",
            "NEXT_BUTTON",
            "THANKS_BUTTON",
        ]:
            if not self.check_and_click_until_found(self.template_images[key], f"{key.replace('_', ' ').title()}"):
                break
        time.sleep(2)
        self.check_and_click_until_found(self.template_images["CROSS_BUTTON"], "Cross button")
        time.sleep(4)

    def check(self, screenshot, template_image, log_message, similarity_threshold=0.8):
        _, similarity = find_subimage(screenshot, template_image)
        log_message = f"{log_message} found - {similarity:.2f}" if similarity > similarity_threshold else f"{log_message} NOT found - {similarity:.2f}"
        self.log_callback(log_message)
        return similarity > similarity_threshold

    def check_and_click(self, screenshot, template_image, log_message, similarity_threshold=0.8):
        position, similarity = find_subimage(screenshot, template_image)
        if similarity > similarity_threshold:
            self.log_and_click(position, f"{log_message} found - {similarity:.2f}")
            return True
        else:
            self.log_callback(f"{log_message} NOT found - {similarity:.2f}")
            return False

    def check_and_click_until_found(self, template_image, log_message, similarity_threshold=0.8, timeout=30):
        start_time = time.time()
        attempts = 0
        max_attempts = 10

        while self.running:
            screenshot = take_screenshot()
            position, similarity = find_subimage(screenshot, template_image)
            self.log_callback(f"Searching... {log_message} - {similarity:.2f}")

            if similarity > similarity_threshold:
                self.log_and_click(position, f"{log_message} found - {similarity:.2f}")
                return True
            elif time.time() - start_time > timeout:
                attempts += 1
                self.log_callback(f"{log_message} not found within timeout. Attempt {attempts}/{max_attempts}.")
                if attempts >= max_attempts:
                    self.log_callback("Max attempts reached. Stopping the bot.")
                    self.stop()
                return False
            else:
                time.sleep(0.5)

    def log_and_click(self, position, message):
        self.log_callback(message)
        click_position(position[0], position[1])
