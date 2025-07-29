from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Initial system prompt
system_prompt = f"""You are {Assistantname}, a highly intelligent, conversational, and helpful AI assistant developed to interact with {Username}. 
Respond in a polite, warm, and slightly casual tone like a human assistant. 
Speak in fluent English, even if the question is in another language. 
Avoid giving time unless specifically asked. Keep your replies friendly but avoid unnecessary details unless prompted.
Avoid referring to training data. Just answer questions naturally and clearly.
"""

SystemChatBot = [
    {"role": "system", "content": system_prompt}
]

# Load existing chat logs or create new
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

# Get current real-time information
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        "Please use this real-time information if needed, \n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )

# Clean up the answer
def AnswerModifier(answer):
    return '\n'.join(line for line in answer.split('\n') if line.strip())

# Main chatbot logic
def Chatbot(query):
    try:
        # Load chat history
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query
        messages.append({"role": "user", "content": query})

        # Create the chat completion request
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        # Collect streamed answer
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "").strip()

        # Save assistant's response
        messages.append({"role": "assistant", "content": answer})
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred. Please try again later."

# Run loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter the question: ")
        print(Chatbot(user_input))
