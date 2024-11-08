import time
import os
from adb_utils import long_press_position, find_subimage, take_screenshot


class BattleActions:
    def __init__(
        self,
        image_processor,
        template_images,
        card_images,
        zoom_card_region,
        number_of_cards_region,
        log_callback,
    ):
        self.log_callback = log_callback
        self.image_processor = image_processor
        self.template_images = template_images
        self.card_images = card_images
        self.zoom_card_region = zoom_card_region
        self.number_of_cards_region = number_of_cards_region

    def check_turn(self, turn_check_region, running):
        self.log_callback("Checking turn...")
        if not running:
            return False
        screenshot1 = self.image_processor.capture_region(turn_check_region)
        time.sleep(1)
        screenshot2 = self.image_processor.capture_region(turn_check_region)

        similarity = self.image_processor.calculate_similarity(screenshot1, screenshot2)
        if similarity < 0.95:
            self.log_callback("It's your turn")
        else:
            if self.image_processor.check_and_click(
                take_screenshot(),
                self.template_images["START_BATTLE_BUTTON"],
                "Start battle button",
            ):
                self.log_callback("First turn")
            self.log_callback("Waiting for opponent's turn...")

        return similarity < 0.95

    def perform_search_battle_actions(self, running, stop, run_event=False):
        if not self.image_processor.check_and_click_until_found(
            self.template_images["VERSUS_SCREEN"],
            'Versus Screen',
            running,
            stop,
            max_attempts=10,
        ):
            return False
        if run_event:
            if not self.image_processor.check_and_click_until_found(
                self.template_images["EVENT_MATCH_SCREEN"],
                'Event Match Screen',
                running,
                stop,
                max_attempts=10,
            ):
                if not self.image_processor.check_and_click_until_found(
                    self.template_images["RANDOM_MATCH_SCREEN"],
                    'Random Match Screen',
                    running,
                    stop,
                    max_attempts=10,
                ):
                    return False
        else:
            if not self.image_processor.check_and_click_until_found(
                self.template_images["RANDOM_MATCH_SCREEN"],
                'Random Match Screen',
                running,
                stop,
                max_attempts=10,
            ):
                return False
        if not self.image_processor.check_and_click_until_found(
            self.template_images["BATTLE_BUTTON"],
            'Battle Button',
            running,
            stop,
            max_attempts=10,
        ):
            return False

    def check_rival_concede(self, screenshot, running, stop):
        self.log_callback("🔍 **Checking if the rival conceded...**")

        # Check if the "Tap to Proceed" button (indicating a concede) is visible
        if self.image_processor.check(
            screenshot, self.template_images["TAP_TO_PROCEED_BUTTON"], "Rival conceded"
        ):
            self.log_callback("✅ **Rival conceded!**")

            # Process buttons to continue the game flow
            for key in ["NEXT_BUTTON", "THANKS_BUTTON"]:
                if not self.image_processor.check_and_click_until_found(
                    self.template_images[key],
                    f"{key.replace('_', ' ').title()}",
                    running,
                    stop,
                ):
                    self.log_callback(f"❌ **{key.replace('_', ' ').title()}** button not found or clicked.")
                    break

            # Allow time for transition after button clicks
            time.sleep(2)

            # Click the 'Cross' button to finalize the process
            self.image_processor.check_and_click_until_found(
                self.template_images["CROSS_BUTTON"], 'Cross button', running, stop
            )
            self.log_callback("✅ **Concede process completed, closing...**")
            time.sleep(4)

        else:
            self.log_callback("❌ **Rival hasn't conceded.**")

    def get_card(self, x, y, duration=1.0):
        self.log_callback(f"📸 **Capturing card** at position ({x}, {y}) for {duration}s...")

        # Define the region for zoomed-in card
        x_zoom_card_region, y_zoom_card_region, w, h = self.zoom_card_region

        # Capture the card image by simulating the press
        card_image = long_press_position(x, y, duration)

        # Log the region being extracted
        self.log_callback(
            f"✂️ **Extracting region**: (x: {x_zoom_card_region}, y: {y_zoom_card_region}), width: {w}, height: {h}"
        )

        # Return the cropped image based on the defined zoom region
        cropped_image = card_image[
            y_zoom_card_region : y_zoom_card_region + h,
            x_zoom_card_region : x_zoom_card_region + w,
        ]

        # Log the success of the card capture
        self.log_callback(f"✅ **Card captured** successfully.")

        return cropped_image
    
    def identify_card(self, zoomed_card_image):
        self.log_callback("🔍 **Identifying card...**")
        
        highest_similarity = 0
        identified_card = None

        # Iterate through all known card templates
        for card_name, template_image in self.card_images.items():
            base_card_name = os.path.splitext(card_name)[0]
            
            # Compare the zoomed image with the current template
            _, similarity = find_subimage(zoomed_card_image, template_image)
            
            # If a match with high similarity is found, store it
            if similarity > 0.8 and similarity > highest_similarity:
                highest_similarity = similarity
                identified_card = base_card_name
                self.log_callback(f"✔️ Found match: {base_card_name} with similarity: {similarity:.2f}")

        # Log the result
        if identified_card:
            self.log_callback(f"🃏 **Card identified**: {identified_card}")
        else:
            self.log_callback("❌ **No matching card found**")

        return identified_card

    def check_number_of_cards(self, card_x, card_y):
        self.log_callback(f"Checking the number of cards...")
        long_press_position(card_x, card_y, 1.5)

        number_image = self.image_processor.capture_region(self.number_of_cards_region)

        number = self.image_processor.extract_number_from_image(number_image)
        self.log_callback(f"Number of cards: {number}")

        return number
