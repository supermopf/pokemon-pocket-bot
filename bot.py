import time
import cv2
import threading
import numpy as np
from adb_utils import connect_to_emulator, click_position, take_screenshot, find_subimage
from constants import (
    BATTLE_SCREEN,
    BATTLE_ALREADY_SCREEN,
    VERSUS_SCREEN,
    RANDOM_MATCH_SCREEN,
    BATTLE_BUTTON,
    MATCH_MENU_BUTTON,
    CONCEDE_BUTTON,
    CONCEDE_ACCEPT_BUTTON,
    TAP_TO_PROCEED_BUTTON,
    NEXT_BUTTON,
    THANKS_BUTTON,
    CROSS_BUTTON,
    TIME_LIMIT_INDICATOR,
    GOING_FIRST_INDICATOR,
    GOING_SECOND_INDICATOR
)

class PokemonBot:
    def __init__(self, app_state, log_callback):
        self.app_state = app_state
        self.log_callback = log_callback
        self.running = False
        self.load_template_images()
        
        self.turn_check_region = (50, 1560, 200, 20)

    def load_template_images(self):
        # Load all template images
        self.template_images = {
            "BATTLE_SCREEN": cv2.imread(BATTLE_SCREEN),
            "BATTLE_ALREADY_SCREEN": cv2.imread(BATTLE_ALREADY_SCREEN),
            "VERSUS_SCREEN": cv2.imread(VERSUS_SCREEN),
            "RANDOM_MATCH_SCREEN": cv2.imread(RANDOM_MATCH_SCREEN),
            "BATTLE_BUTTON": cv2.imread(BATTLE_BUTTON),
            "MATCH_MENU_BUTTON": cv2.imread(MATCH_MENU_BUTTON),
            "CONCEDE_BUTTON": cv2.imread(CONCEDE_BUTTON),
            "CONCEDE_ACCEPT_BUTTON": cv2.imread(CONCEDE_ACCEPT_BUTTON),
            "TAP_TO_PROCEED_BUTTON": cv2.imread(TAP_TO_PROCEED_BUTTON),
            "NEXT_BUTTON": cv2.imread(NEXT_BUTTON),
            "THANKS_BUTTON": cv2.imread(THANKS_BUTTON),
            "CROSS_BUTTON": cv2.imread(CROSS_BUTTON),
            "TIME_LIMIT_INDICATOR": cv2.imread(TIME_LIMIT_INDICATOR),
            "GOING_FIRST_INDICATOR": cv2.imread(GOING_FIRST_INDICATOR),
            "GOING_SECOND_INDICATOR": cv2.imread(GOING_SECOND_INDICATOR)
        }

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
            #if not self.check_and_click(screenshot, self.template_images["BATTLE_ALREADY_SCREEN"], "Battle already screen"):
            #    self.check_and_click(screenshot, self.template_images["BATTLE_SCREEN"], "Battle screen")
            #time.sleep(1)
            #self.perform_search_battle_actions()
            self.check_and_click_until_found(self.template_images["TIME_LIMIT_INDICATOR"], "Time limit indicator")
            screenshot = take_screenshot()
            if not self.check(screenshot, self.template_images["GOING_FIRST_INDICATOR"], "Going first"):
                self.check(screenshot, self.template_images["GOING_SECOND_INDICATOR"], "Going second")


            # Check if it is the player's turn
            if self.check_turn():
                self.log_callback("It's your turn! Taking action...")
                self.play_turn()
            else:
                self.log_callback("Waiting for opponent's turn...")
                time.sleep(1)

    def perform_search_battle_actions(self):
        for key in [
            "VERSUS_SCREEN",
            "RANDOM_MATCH_SCREEN",
            "BATTLE_BUTTON",
        ]:
            if not self.check_and_click_until_found(self.template_images[key], f"{key.replace('_', ' ').title()}"):
                break

    def play_turn(self):
        # Logic to select and play cards goes here
        self.log_callback("Playing turn actions...")
        # Example: self.check_and_click_until_found(self.template_images["SOME_CARD"], "Card X")

    def check_turn(self):
        screenshot1 = self.capture_region(self.turn_check_region)
        time.sleep(1)
        screenshot2 = self.capture_region(self.turn_check_region)

        similarity = self.calculate_similarity(screenshot1, screenshot2)
        cv2.imwrite("debug_screenshot1.png", screenshot1)
        cv2.imwrite("debug_screenshot2.png", screenshot2)
        self.log_callback(f"Turn check similarity: {similarity:.2f}")

        return similarity < 0.95

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
