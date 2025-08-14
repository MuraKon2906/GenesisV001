import os
from genesisv001._core import hello_from_bin
from genesisv001._core import genesis_translate
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


def main() -> None:
    print(hello_from_bin())
    # Test for Translation
    print(genesis_translate(input="Hallo, mein Name ist Shaan, was ist dein?"))
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=" Explain whats the mitochondria in one line"
    )
    print(response.text)
