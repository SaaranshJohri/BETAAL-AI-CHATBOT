import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load voice config from .env
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Constants
SPEECH_FILE = r"Data\speech.mp3"

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# Async function to generate TTS audio file
async def TextToAudioFile(text):
    if os.path.exists(SPEECH_FILE):
        os.remove(SPEECH_FILE)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(SPEECH_FILE)

# Synchronous wrapper to play speech
def TTS(text, func=lambda r=None: True):
    try:
        # Handle environments where event loop already running
        try:
            asyncio.run(TextToAudioFile(text))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(TextToAudioFile(text))

        # Initialize mixer only once
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(SPEECH_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Wrapper to trim long text and notify via chat
def TexttoSpeech(text, func=lambda r=None: True):
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    text = str(text).strip()

    # If text is long, read part aloud and notify
    if len(text.split()) > 60 or len(text) > 250:
        parts = text.split(".")
        short_text = ". ".join(parts[:2]).strip() + "."
        tail_msg = random.choice(responses)
        TTS(f"{short_text} {tail_msg}", func)
    else:
        TTS(text, func)

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        if not user_input.strip():
            break
        TexttoSpeech(user_input)
