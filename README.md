🧠 BETAAL AI – Fast Conversational Voice Assistant Powered by Groq LLMs
BETAAL AI is a real-time voice-based AI assistant built using Groq’s ultra-fast LLM API. It delivers natural, human-like conversations with lightning-fast response times, creating a fluid and engaging voice interaction experience.

⚙️ Technologies: Python, Groq API, LLama3 / Mixtral, SpeechRecognition, pyttsx3, dotenv

🎯 Features
🎙️ Real-Time Voice Chat: Speak naturally with the assistant and get instant voice responses.

⚡️ Groq-Powered Speed: Leveraging Groq's LPU-powered inference to deliver some of the fastest LLM response times in the world.

🧠 LLM Intelligence: Uses powerful open-weight models like LLaMA 3-70B or Mixtral 8x7B to provide intelligent and context-aware responses.

🗣 Text-to-Speech (TTS): Uses pyttsx3 to vocalize responses for a smooth conversational feel.

📝 Session Memory: Maintains context across turns using chat history.

💡 Natural Tone: Designed with a warm, expressive, and human-like speaking style.

🔧 How It Works
Speech Recognition: User speaks via microphone, and the SpeechRecognition library transcribes the audio.

Groq LLM API: The transcribed prompt is sent to Groq’s API (using llama3-70b or similar) for response generation.

Text-to-Speech: The assistant’s reply is spoken out loud using a TTS engine (pyttsx3).

Chat Loop: The conversation continues with real-time voice input and output.

🛠 Setup Instructions
✅ Prerequisites
Python 3.8+

Groq API Key (get from https://console.groq.com)

Working microphone for input

📦 Installation
Clone the repository

bash
Copy
Edit
git clone https://github.com/yourusername/betaal-ai.git
cd betaal-ai
Create & activate virtual environment

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate    # Windows
# OR
source venv/bin/activate # macOS/Linux
Install requirements

bash
Copy
Edit
pip install -r requirements.txt
Configure environment variables

Create a .env file:

ini
Copy
Edit
GROQ_API_KEY=your_groq_api_key_here
🚀 Run the Assistant
bash
Copy
Edit
python Main.py
Say things like:

"Hi BETAAL, what’s the capital of Japan?"
"Tell me a fun fact about space!"

📁 Project Structure
bash
Copy
Edit
betaal-ai/
├── Main.py                 # Entry point for the assistant
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── utils/
│   ├── groq_llm.py         # LLM integration via Groq
│   ├── speech_to_text.py   # Converts speech to text
│   └── text_to_speech.py   # Converts text to speech
└── README.md               # Project documentation
🚀 Why Groq?
🧠 Open-weight models (like Meta's LLaMA or Mistral's Mixtral)

⚡ Inference latency under 1 ms/token

💵 Free access with API key

🧪 Great for research and experimentation

🔮 Future Enhancements
Integration with tools like web search, weather, and local file handling

GUI interface (using Tkinter or PyQt)

Multiple voice options and personalities

Multi-language support

🙌 Credits
Groq – for the blazing-fast LLM inference engine

Meta AI – for LLaMA open models

Mistral AI – for Mixtral models

SpeechRecognition – for converting voice to text

pyttsx3 – for voice output
