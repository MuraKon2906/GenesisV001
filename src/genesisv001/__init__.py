import os
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from luma.core.render import canvas
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

    def draw(self, input):
        with canvas(self.device) as draw:
            draw.text((20, 20), input, fill="white")


class Casy:
    def __init__(self) -> None:
        self.inst_display = Display()

    def display_test(self, test_content):
        inst = self.inst_display
        inst.draw(input=test_content)

    def translation_app(self):
        while True:
            query = input("Enter the text for translation: ")
            if query == "q":
                print("Goodbye")
                break

            if query != "q":
                print("Translating")
                print(genesis_translate(query))

    def ai_scheduler(self):
        tasks = input("Enter your tasks : ")
        schedule = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""{tasks} prepare me a consise easy to read with minimum generation optimised schedule that helps me with productivity .
            eg : 

            Here you go Boss man : 
            Time | Task | bried desc less than 5 words

            """,
        )
        print(remove_gen_waste(schedule.text))

    def teleprompter(self):
        content = input("Enter the title of the speech : ")

        script = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
            {content} 
            Generate a very concise, motivational, and engaging speech based strictly on the above content. 
            The speech should be simple, and easy to deliver,make the speech upto 20 lines at least . 
            Always start the output exactly with: 

            "Here you go boss man:"

            Do not add any extra text, disclaimers, or introductions beyond the requested speech. 
            """,
        )
        print(remove_gen_waste(script.text))


def main() -> None:
    inst = Casy()
    print(hello_from_bin())
    choice = int(input("what you want boss man ?"))
    if choice == 1:
        print("Welcome to the Translation App")
        inst.translation_app()

    elif choice == 2:
        inst.ai_scheduler()
    elif choice == 3:
        inst.teleprompter()

    display_test = "Hello Nandha !"
    inst.display_test(test_content=display_test)
