# --- All your existing imports ---
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.model import FirstLayerDMM
from Backend.realtimesearchengine import realtimesearchengine
from Backend.automation import Automation
from Backend.speechtotext import SpeechRecognition
from Backend.chatbot import Chatbot
from Backend.texttospeech import TexttoSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys

# --- Constants & Setup ---
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f"""{Username} : Hello {Assistantname}, how are you?
{Assistantname} : Welcome {Username}, I am doing well. How may I help you?"""

process_list = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\Chatlog.json', "r", encoding='utf-8') as File:
            if len(File.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath('responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except Exception as e:
        print(f"[ERROR] ChatLog load failed: {e}")


def ReadChatlogJson():
    with open(r'Data\Chatlog.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def ChatLogIntegration():
    json_data = ReadChatlogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = Username if entry["role"] == "user" else Assistantname
        formatted_chatlog += f"{role}: {entry['content']}\n"
    with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
            Data = File.read()
        if Data.strip():
            with open(TempDirectoryPath('responses.data'), "w", encoding='utf-8') as File:
                File.write(Data)
    except Exception as e:
        print(f"[ERROR] GUI chat display failed: {e}")


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")
    Decision = FirstLayerDMM(Query)

    print("\nDecision :", Decision, "\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    if isinstance(Decision, str):
        Decision = [Decision]

    for query in Decision:
        if "generate" in query.lower():
            ImageGenerationQuery = query
            ImageExecution = True
            break

    for query in Decision:
        if not TaskExecution and any(query.lower().startswith(func.lower()) for func in Functions):
            print("[DEBUG] Detected automation function call.")
            run(Automation(Decision))
            TaskExecution = True

    if ImageExecution and ImageGenerationQuery:
        try:
            print(f"[DEBUG] Triggering image generation for prompt: {ImageGenerationQuery}")
            with open(r"Frontend\Files\imagegen.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            p1 = subprocess.Popen(
                ["python", r"Backend\imagegen.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            process_list.append(p1)

            stdout, stderr = p1.communicate(timeout=120)
            print("[IMAGEGEN OUTPUT]", stdout.decode())
            print("[IMAGEGEN ERRORS]", stderr.decode())

        except subprocess.TimeoutExpired:
            p1.kill()
            print("[ERROR] imagegen.py timed out.")
        except Exception as e:
            print(f"[ERROR] Failed to start image generation subprocess: {e}")

    if R:
        SetAssistantStatus("Searching...")
        if Mearged_query.strip():
            Answer = realtimesearchengine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TexttoSpeech(Answer)
        else:
            ShowTextToScreen(f"{Assistantname} : Sorry, I didn't catch that.")
        return True

    for Queries in Decision:
        if "general" in Queries:
            SetAssistantStatus("Thinking ...")
            QueryFinal = Queries.replace("general ", "")
            if QueryFinal.strip():
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering ...")
                TexttoSpeech(Answer)
            else:
                ShowTextToScreen(f"{Assistantname} : Sorry, I didn't understand that.")
            return True

        elif "exit" in Queries:
            QueryFinal = "Okay, Bye!"
            Answer = Chatbot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TexttoSpeech(Answer)
            sys.exit(1)


def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        elif "Available.." not in GetAssistantStatus():
            SetAssistantStatus("Available..")
        else:
            sleep(0.1)


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
