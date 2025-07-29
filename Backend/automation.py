from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIkey = env_vars.get("GroqAPIKey")

# Define CSS classes for parsing HTML content
classes = ["zCubwf", "hgKCIC", "LTKOO s?Pric", "zGLcw", "gsrt vk bk FzvMsb YwPhmf", "pcIqee",
           "tw-Data-text tw-text-small tw-ta", "I26rdc", "O5uR6d LTKOO", "vI2Y6d",
           "webanswers-webanswers_table_webanswers-table", "dD0No ikB4Bb gsrt", "sXLa0e",
           "lwkFke", "VQF4g", "qvJwpe", "kno-rdesc", "SPZz6B"]

# User-agent string
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIkey)

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]

messages = []

SystemChatBot = {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Your Assistant')}, You're a content writer. You have to write content like letter"}

# Google search function
def GoogleSearch(topic):
    search(topic)
    return True

# Function to generate and display content
def Content(topic):

    def OpenNotepad(file):
        subprocess.Popen(['notepad.exe', file])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[SystemChatBot] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        messages.append({"role": "assistant", "content": answer})
        return answer.replace("</s>", "")

    topic = topic.replace("content ", "")
    content_by_ai = ContentWriterAI(topic)

    filename = rf"Data\{topic.lower().replace(' ', '')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    OpenNotepad(filename)
    return True

# YouTube search function
def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True

# YouTube play function
def PlayYoutube(query):
    playonyt(query)
    return True

# Open app function
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWcNkb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

# Close app function
def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

# System controls
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume unmute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    action = actions.get(command)
    if action:
        action()
        return True
    return False

# Translate and execute commands
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        cmd = command.lower()
        if cmd.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, cmd.removeprefix("open ")))
        elif cmd.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd.removeprefix("close ")))
        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd.removeprefix("play ")))
        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd.removeprefix("content ")))
        elif cmd.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search ")))
        elif cmd.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd.removeprefix("youtube search ")))
        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd.removeprefix("system ")))
        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Automation wrapper
async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True