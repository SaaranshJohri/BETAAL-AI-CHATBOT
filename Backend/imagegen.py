import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
import json

# HuggingFace API setup
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Display generated images
def open_images(prompt):
    folder_path = r"Data"
    prompt_safe = prompt.replace(" ", "_")

    for i in range(1, 5):
        image_path = os.path.join(folder_path, f"{prompt_safe}{i}.jpg")
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue
        try:
            img = Image.open(image_path)
            img.verify()  # Check integrity
            img = Image.open(image_path)  # Reopen to actually use
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except Exception as e:
            print(f"Unable to open {image_path}: {e}")


# Query the Hugging Face API asynchronously
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Generate multiple images asynchronously
import json

async def generate_images(prompt: str):
    prompt_safe = prompt.replace(" ", "_")
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, 4K, ultra-sharp, high detail, seed={randint(0, 1_000_000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        try:
            # Try decoding as JSON to catch error responses
            decoded = image_bytes.decode("utf-8")
            if decoded.startswith("{") or decoded.startswith("["):
                json_data = json.loads(decoded)
                print(f"Error from API for image {i+1}: {json_data}")
                continue
        except UnicodeDecodeError:
            # It is binary (likely a real image)
            pass

        filename = os.path.join("Data", f"{prompt_safe}{i+1}.jpg")
        with open(filename, "wb") as f:
            f.write(image_bytes)


# Synchronous wrapper
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Watch loop for file signal
if __name__ == "__main__":
    while True:
        try:
            # Read prompt and status from data file
            with open(r"Frontend\Files\imagegen.data", "r") as f:
                Data: str = f.read().strip()

            if not Data:
                sleep(1)
                continue

            Prompt, Status = Data.split(",")

            if Status.strip() == "True":
                print(f"Generating Images for: {Prompt}")
                GenerateImages(Prompt)

                # Reset status after generation
                with open(r"Frontend\Files\imagegen.data", "w") as f:
                    f.write(f"{Prompt},False")

                print("Image generation complete.")
                break
            else:
                sleep(1)

        except:
            pass
