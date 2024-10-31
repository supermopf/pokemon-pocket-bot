import time
import cv2
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
    CROSS_BUTTON
)

class PokemonBot:
    def __init__(self, app_state, log_callback):
        self.app_state = app_state
        self.log_callback = log_callback
        self.running = False
        self.BATTLE_SCREEN = cv2.imread(BATTLE_SCREEN)
        self.BATTLE_ALREADY_SCREEN = cv2.imread(BATTLE_ALREADY_SCREEN)
        self.VERSUS_SCREEN = cv2.imread(VERSUS_SCREEN)
        self.RANDOM_MATCH_SCREEN = cv2.imread(RANDOM_MATCH_SCREEN)
        self.BATTLE_BUTTON = cv2.imread(BATTLE_BUTTON)
        self.MATCH_MENU_BUTTON = cv2.imread(MATCH_MENU_BUTTON)
        self.CONCEDE_BUTTON = cv2.imread(CONCEDE_BUTTON)
        self.CONCEDE_ACCEPT_BUTTON = cv2.imread(CONCEDE_ACCEPT_BUTTON)
        self.TAP_TO_PROCEED_BUTTON = cv2.imread(TAP_TO_PROCEED_BUTTON)
        self.NEXT_BUTTON = cv2.imread(NEXT_BUTTON)
        self.THANKS_BUTTON = cv2.imread(THANKS_BUTTON)
        self.CROSS_BUTTON = cv2.imread(CROSS_BUTTON)

    def start(self):
        if not self.app_state.program_path:
            self.log_callback("Please select emulator path first.")
            return
        self.running = True
        self.connect_and_run()

    def stop(self):
        self.running = False

    def connect_and_run(self):
        connect_to_emulator(self.app_state.emulator_name)
        self.log_callback("Connected to emulator")
        self.run_script()

    def run_script(self):
        screenshot = take_screenshot()
        if not self.check_and_click(screenshot, self.BATTLE_ALREADY_SCREEN, "Battle already screen"):
            self.check_and_click(screenshot, self.BATTLE_SCREEN, "Battle screen")
        self.check_and_click_until_found(self.VERSUS_SCREEN, "Versus screen")
        self.check_and_click_until_found(self.RANDOM_MATCH_SCREEN, "Random match screen")
        self.check_and_click_until_found(self.BATTLE_BUTTON, "Battle button")
        self.check_and_click_until_found(self.MATCH_MENU_BUTTON, "Match menu button")
        self.check_and_click_until_found(self.CONCEDE_BUTTON, "Concede button")
        self.check_and_click_until_found(self.CONCEDE_ACCEPT_BUTTON, "Concede accept button")
        self.check_and_click_until_found(self.TAP_TO_PROCEED_BUTTON, "Tap to proceed button")
        self.check_and_click_until_found(self.NEXT_BUTTON, "Next button")
        self.check_and_click_until_found(self.THANKS_BUTTON, "Thanks button")
        self.check_and_click_until_found(self.CROSS_BUTTON, "Cross button")

    def check(self, screenshot, template_image, log_message, similarity_threshold=0.8):
        _, similarity = find_subimage(screenshot, template_image)
        if similarity > similarity_threshold:
            self.log_callback(f"{log_message} found - {similarity:.2f}")
            return True
        else:
            self.log_callback(f"{log_message} NOT found - {similarity:.2f}")
            return False      

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

        while True:
            screenshot = take_screenshot()
            position, similarity = find_subimage(screenshot, template_image)
            self.log_callback(f"Searching... {log_message} - Similarity: {similarity:.2f}")

            if similarity > similarity_threshold:
                self.log_and_click(position, f"{log_message} found - Similarity: {similarity:.2f}")
                return True
            elif time.time() - start_time > timeout:
                self.log_callback(f"{log_message} not found within timeout.")
                return False
            else:
                time.sleep(0.5) 

    def log_and_click(self, position, message):
        self.log_callback(message)
        click_position(position[0], position[1])
        ##time.sleep(1)
