import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def get_plan_from_ai(task):
    print("🧠 Contacting OpenRouter...")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # you can also try "mistralai/mixtral-8x7b" or other models
        messages=[
            {
                "role": "system",
                "content": (
                    "You're a smart task planner agent. Given a user request, return:"
                    "\n\nPLAN: Step-by-step plan"
                    "\nCOMMANDS: List of shell commands to execute"
                    "\nFILES: Files to create in format:\n--- filename.py:\ncode"
                )
            },
            {"role": "user", "content": task}
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content
