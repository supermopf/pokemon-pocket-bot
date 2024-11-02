import time

from image_utils import ImageProcessor

class BattleActions:
    def __init__(self, image_processor, template_images, log_callback):
        self.log_callback = log_callback
        self.image_processor = image_processor
        self.template_images = template_images

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