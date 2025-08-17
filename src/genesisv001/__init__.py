import os
import time
import threading
import speech_recognition as sr
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from luma.core.render import canvas
from PIL import ImageFont
from genesisv001._core import hello_from_bin
from genesisv001._core import genesis_translate
from genesisv001._core import remove_gen_waste
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


class Display:
    def __init__(self) -> None:
        serial = spi(
            device=0, port=0, gpio_DC=25, gpio_RST=27
        )  # CE0=GPIO8, DC=GPIO25, RST=GPIO27
        self.device = ssd1309(serial, width=128, height=64)
        # Try to load a font, fallback to default if not available
        try:
            self.font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10
            )
            self.title_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12
            )
        except:
            self.font = ImageFont.load_default()
            self.title_font = ImageFont.load_default()

    def draw_text(self, text, x=0, y=0, font=None):
        """Draw text with word wrapping"""
        if font is None:
            font = self.font

        with canvas(self.device) as draw:
            words = text.split(" ")
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= 128:  # Width fits
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Draw lines with proper spacing
            line_height = 12
            for i, line in enumerate(lines[:5]):  # Max 5 lines for 64px height
                draw.text((x, y + i * line_height), line, font=font, fill="white")

    def draw_menu(self, title, options, selected=0):
        """Draw a menu with title and options"""
        with canvas(self.device) as draw:
            # Draw title
            draw.text((5, 0), title, font=self.title_font, fill="white")
            draw.line([(0, 15), (128, 15)], fill="white")

            # Draw options
            for i, option in enumerate(options):
                y_pos = 20 + (i * 12)
                if i == selected:
                    # Highlight selected option
                    draw.rectangle([(0, y_pos - 2), (128, y_pos + 10)], fill="white")
                    draw.text((5, y_pos), f"> {option}", font=self.font, fill="black")
                else:
                    draw.text((5, y_pos), f"  {option}", font=self.font, fill="white")

    def draw_status(self, message, progress=None):
        """Draw status message with optional progress indicator"""
        with canvas(self.device) as draw:
            # Draw message
            self.draw_text(message, 5, 10)

            # Draw progress bar if provided
            if progress is not None:
                bar_width = int(118 * progress)  # 118 = 128 - 10 (margins)
                draw.rectangle([(5, 50), (123, 58)], outline="white")
                if bar_width > 0:
                    draw.rectangle([(6, 51), (5 + bar_width, 57)], fill="white")

    def draw_listening_animation(self):
        """Draw animated listening indicator"""

        def animate():
            for i in range(10):  # Animate for a few seconds
                with canvas(self.device) as draw:
                    draw.text(
                        (20, 10), "🎤 LISTENING", font=self.title_font, fill="white"
                    )

                    # Draw sound waves
                    center_x, center_y = 64, 35
                    for j in range(3):
                        radius = 10 + (j * 8) + (i % 4) * 2
                        draw.ellipse(
                            [
                                (center_x - radius, center_y - radius),
                                (center_x + radius, center_y + radius),
                            ],
                            outline="white",
                        )

                    draw.text(
                        (25, 50), "Say something...", font=self.font, fill="white"
                    )
                time.sleep(0.3)

        # Run animation in a separate thread
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()


class Casy:
    def __init__(self) -> None:
        self.inst_display = Display()
        self.r = sr.Recognizer()
        self.r.energy_threshold = 300  # Adjust based on your environment
        self.r.pause_threshold = (
            1  # Seconds of non-speaking audio before a phrase is complete
        )

        # Menu options
        self.main_menu = [
            "Translation App",
            "AI Scheduler",
            "Teleprompter",
            "Display Test",
            "Exit",
        ]

    def speech_to_text(self, prompt="Listening..."):
        """Convert speech to text with better error handling"""
        self.inst_display.draw_status(prompt)
        self.inst_display.draw_listening_animation()

        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.r.adjust_for_ambient_noise(source, duration=1)
            print(f"{prompt} - Speak now!")

            try:
                # Listen with timeout
                audio_text = self.r.listen(source, timeout=10, phrase_time_limit=10)
                self.inst_display.draw_status("Processing...")

                # Recognize speech
                result = self.r.recognize_google(audio_text)
                print(f"You said: {result}")
                return result.lower()

            except sr.WaitTimeoutError:
                error_msg = "Timeout - No speech detected"
                print(error_msg)
                self.inst_display.draw_status(error_msg)
                time.sleep(2)
                return None

            except sr.UnknownValueError:
                error_msg = "Could not understand audio"
                print(error_msg)
                self.inst_display.draw_status(error_msg)
                time.sleep(2)
                return None

            except Exception as e:
                error_msg = f"Error: {str(e)[:20]}..."
                print(error_msg)
                self.inst_display.draw_status(error_msg)
                time.sleep(2)
                return None

    def voice_menu_selection(self):
        """Voice-controlled menu selection"""
        selected = 0

        while True:
            self.inst_display.draw_menu("CASY Assistant", self.main_menu, selected)

            self.inst_display.draw_status(
                "Say: 'next', 'previous', 'select', or option name"
            )
            time.sleep(2)

            command = self.speech_to_text("Menu Navigation")

            if command is None:
                continue

            if "next" in command or "down" in command:
                selected = (selected + 1) % len(self.main_menu)
            elif "previous" in command or "up" in command or "back" in command:
                selected = (selected - 1) % len(self.main_menu)
            elif "select" in command or "choose" in command or "ok" in command:
                return selected + 1
            elif "exit" in command or "quit" in command:
                return 5
            else:
                # Try to match command with menu option
                for i, option in enumerate(self.main_menu):
                    if any(word in command for word in option.lower().split()):
                        return i + 1

    def translation_app(self):
        """Voice-controlled translation app"""
        self.inst_display.draw_status("Translation App", 0.2)

        while True:
            self.inst_display.draw_status("Say text to translate or 'quit' to exit")
            time.sleep(2)

            query = self.speech_to_text("What to translate?")

            if query is None:
                continue

            if "quit" in query or "exit" in query:
                self.inst_display.draw_status("Exiting translator...")
                time.sleep(2)
                break

            self.inst_display.draw_status("Translating...", 0.7)

            try:
                translation = genesis_translate(query)
                self.inst_display.draw_text(f"Translation:\n{translation}")
                time.sleep(5)  # Show result for 5 seconds
            except Exception as e:
                self.inst_display.draw_status(f"Translation error: {str(e)[:15]}...")
                time.sleep(3)

    def ai_scheduler(self):
        """Voice-controlled AI scheduler"""
        self.inst_display.draw_status("AI Scheduler", 0.3)
        time.sleep(1)

        self.inst_display.draw_status("Describe your tasks to schedule")
        time.sleep(2)

        tasks = self.speech_to_text("What tasks need scheduling?")

        if tasks is None:
            return

        self.inst_display.draw_status("Creating schedule...", 0.6)

        try:
            schedule = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=f"""{tasks} prepare me a concise easy to read with minimum generation optimised schedule that helps me with productivity.
                eg : 
                Here you go Boss man : 
                Time | Task | brief desc less than 5 words
                """,
            )

            result = remove_gen_waste(schedule.text)
            print(result)  # Print to console for full view

            # Show on display with scrolling if needed
            self.inst_display.draw_text(f"Schedule created!\nCheck console for details")
            time.sleep(5)

        except Exception as e:
            self.inst_display.draw_status(f"Scheduler error: {str(e)[:15]}...")
            time.sleep(3)

    def teleprompter(self):
        """Voice-controlled teleprompter"""
        self.inst_display.draw_status("Teleprompter", 0.4)
        time.sleep(1)

        self.inst_display.draw_status("Say the speech title/topic")
        time.sleep(2)

        content = self.speech_to_text("What's your speech topic?")

        if content is None:
            return

        self.inst_display.draw_status("Generating speech...", 0.8)

        try:
            script = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=f"""
                {content} 
                Generate a very concise, motivational, and engaging speech based strictly on the above content. 
                The speech should be simple, and easy to deliver, make the speech up to 20 lines at least. 
                Always start the output exactly with: 
                "Here you go boss man:"
                Do not add any extra text, disclaimers, or introductions beyond the requested speech. 
                """,
            )

            result = remove_gen_waste(script.text)
            print(result)  # Print to console for full speech

            self.inst_display.draw_text(
                "Speech generated!\nCheck console for full text"
            )
            time.sleep(5)

        except Exception as e:
            self.inst_display.draw_status(f"Speech error: {str(e)[:15]}...")
            time.sleep(3)

    def display_test(self):
        """Test display functionality"""
        test_messages = [
            "Hello Nandha!",
            "Display test successful",
            "Audio input working",
            "OLED display enhanced",
        ]

        for i, msg in enumerate(test_messages):
            self.inst_display.draw_status(msg, (i + 1) / len(test_messages))
            time.sleep(2)


def main() -> None:
    inst = Casy()

    # Show welcome message
    inst.inst_display.draw_status("Initializing CASY...")
    time.sleep(2)

    print(hello_from_bin())
    inst.inst_display.draw_text("Welcome to CASY!\nVoice Assistant Ready")
    time.sleep(3)

    while True:
        choice = inst.voice_menu_selection()

        if choice == 1:
            inst.translation_app()
        elif choice == 2:
            inst.ai_scheduler()
        elif choice == 3:
            inst.teleprompter()
        elif choice == 4:
            inst.display_test()
        elif choice == 5:
            inst.inst_display.draw_status("Goodbye!")
            time.sleep(2)
            break

        # Return to menu after each function
        inst.inst_display.draw_status("Returning to menu...")
        time.sleep(2)


if __name__ == "__main__":
    main()
