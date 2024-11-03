import time
import os
from adb_utils import long_press_position, find_subimage
from image_utils import ImageProcessor

class BattleActions:
    def __init__(self, image_processor, template_images, card_images, zoom_card_region, number_of_cards_region, log_callback):
        self.log_callback = log_callback
        self.image_processor = image_processor
        self.template_images = template_images
        self.card_images = card_images
        self.zoom_card_region = zoom_card_region
        self.number_of_cards_region = number_of_cards_region

    def check_turn(self, turn_check_region, running): 
        if not running:
            return False
        screenshot1 = self.image_processor.capture_region(turn_check_region)
        time.sleep(1)
        screenshot2 = self.image_processor.capture_region(turn_check_region)

        similarity = self.image_processor.calculate_similarity(screenshot1, screenshot2)
        if similarity < 0.95:
            self.log_callback("It's your turn! Taking action...")
        else:
            self.log_callback("Waiting for opponent's turn...")

        return similarity < 0.95
    
    def perform_search_battle_actions(self, running, stop):
        for key in [
            "VERSUS_SCREEN",
            "RANDOM_MATCH_SCREEN",
            "BATTLE_BUTTON",
        ]:
            if not self.image_processor.check_and_click_until_found(self.template_images[key], f"{key.replace('_', ' ').title()}", running, stop):
                break

    def check_rival_concede(self, screenshot, running, stop):
        self.log_callback(f"Checking if the rival conceded...")
        if self.image_processor.check(screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Rival conceded"):
            for key in [
                "NEXT_BUTTON",
                "THANKS_BUTTON",
            ]:
                if not self.image_processor.check_and_click_until_found(self.template_images[key], f"{key.replace('_', ' ').title()}", running, stop):
                    break
            time.sleep(2)
            self.image_processor.check_and_click_until_found(self.template_images["CROSS_BUTTON"], "Cross button", running, stop)
            time.sleep(4)
        else:
            self.log_callback(f"Rival hasn't conceded")    
    
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
        self.log_callback(f"Checking the number of cards...")
        long_press_position(card_x, card_y, 1.5)
        
        number_image = self.image_processor.capture_region(self.number_of_cards_region)
        
        number = self.image_processor.extract_number_from_image(number_image)
        self.log_callback(f"Number of cards: {number}")
        
        return number