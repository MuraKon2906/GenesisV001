import os
from genesisv001._core import hello_from_bin
from genesisv001._core import genesis_translate
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


class Casy:
    def __init__(self) -> None:
        pass

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
        print(schedule.text)

    def teleprompter(self):
        pass


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
    # print(genesis_translate(input="Hallo, mein Name ist Shaan, was ist dein?"))
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash-lite",
    #     contents=" Explain whats the mitochondria in one line",
    # )
    # print(response.text)
