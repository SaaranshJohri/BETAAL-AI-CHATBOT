from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt

# Load language from .env
env_vars = dotenv_values(".env")
inputlang = env_vars.get("InputLanguage", "en-US")

# Create HTML for speech recognition
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = "{inputlang}";
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>'''

# Write the HTML file
html_path = os.path.join("Data", "Voice.html")
os.makedirs("Data", exist_ok=True)
with open(html_path, "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# Setup Selenium Chrome driver
chrome_options = Options()
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Optional: remove for testing

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Paths
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Write assistant status to file
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

# Proper punctuation for question/statement
def QueryModifier(query):
    new_query = query.strip().lower()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's"]

    is_question = any(new_query.startswith(qw) for qw in question_words)
    punctuated = new_query.rstrip(".!?") + ("?" if is_question else ".")
    return punctuated.capitalize()

# Translate any language to English
def UniversalTranslator(text):
    translated = mt.translate(text, "en", "auto")
    return translated.strip().capitalize()

# Perform speech recognition via browser
def SpeechRecognition():
    file_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    driver.get(file_url)
    driver.find_element(By.ID, "start").click()

    print("Listening... Speak now.")
    time.sleep(5)  # Wait to allow recognition to happen

    while True:
        try:
            text = driver.find_element(By.ID, "output").text
            if text.strip():
                driver.find_element(By.ID, "end").click()

                if "en" in inputlang.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
        except Exception as e:
            print("Error during speech recognition:", e)
            break

# Run loop
if __name__ == "__main__":
    while True:
        query = SpeechRecognition()
        print("Recognized:", query)
