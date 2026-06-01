from dotenv import load_dotenv
import os
from openai import OpenAI, AzureOpenAI
from tools import get_air_quality
from retriever import retrieve
import json

load_dotenv()

PROFILE = os.environ.get("LLM_PROFILE", "cloud")


def get_client():
    if PROFILE == "cloud":
        return AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://cds-ds-openai-001-x.openai.azure.com/",
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )
    else:
        return OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )


def get_model_name():
    if PROFILE == "cloud":
        return "gpt-5.4-nano"
    else:
        return "gemma3:e4b"


messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. Use the air quality tool when user asks "
            "about pollution. When available, use retrieved documents to answer questions."
        ),
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_air_quality",
            "description": "Get air pollution data for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name like Bangalore, Delhi, Mumbai",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


def run_agent(user_input):
    client = get_client()
    model = get_model_name()

    context_chunks = retrieve(user_input, k=3)
    context = "\n".join(context_chunks) if context_chunks else ""

    augmented_input = user_input
    if context:
        augmented_input = f"Retrieved context:\n{context}\n\nUser query: {user_input}"

    messages.append({"role": "user", "content": augmented_input})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments or "{}")

        city = args.get("city", "bangalore")
        result = get_air_quality(city)

        messages.append(msg)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            }
        )

        final = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        reply = final.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply

    reply = msg.content or "I couldn't generate a response."
    messages.append({"role": "assistant", "content": reply})
    return reply
