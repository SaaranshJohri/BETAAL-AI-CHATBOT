from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

system = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load or create chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

# Perform a Google search
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    answer += "[end]"
    return answer

# Clean answer
def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# System prompts
SystemChatbot = [
    {"role": "system", "content": system},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Real-time information
def Information():
    now = datetime.datetime.now()
    return (
        "Use This real time information if needed: \n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} : {now.strftime('%M')} : {now.strftime('%S')}\n"
    )

# Main chatbot handler
def realtimesearchengine(prompt):
    global messages, SystemChatbot

    messages.append({"role": "user", "content": prompt})

    # Append Google Search as system context
    SystemChatbot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Append real-time info
    chat_messages = SystemChatbot + [{"role": "system", "content": Information()}] + messages

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        # Remove the last system entry to avoid pollution
        SystemChatbot.pop()

# Entry point
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(realtimesearchengine(prompt))
