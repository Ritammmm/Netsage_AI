import os
import json
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def create_prompt(symptom, topology, evidence):

    prompt = f"""
You are NetSage AI,
a Cisco network troubleshooting assistant.

Analyze the network problem using only the information provided.

Symptom:
{symptom}

Topology:
{topology}

Evidence:
{evidence}

Return only valid JSON.

Required fields:

root_cause
confidence
evidence
osi_layer
next_command
fix_steps
human_review

Rules:

1. Identify the most likely root cause from the available evidence.
2. Do not invent evidence that is not provided.
3. Clearly mention uncertainty when the evidence is insufficient.
4. Recommend a diagnostic command when more verification is needed.
5. Do not apply configuration changes automatically.
6. Human approval is required before applying any fix.
"""

    return prompt


def diagnose(symptom, topology, evidence):

    prompt = create_prompt(
        symptom,
        topology,
        evidence
    )

    # Primary model
    models = [
        "gemini-3.8-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash"
    ]

    for model in models:

        print(f"\nTrying model: {model}", flush=True)

        for attempt in range(1, 3):

            try:

                print(
                    f"Attempt {attempt}/2...",
                    flush=True
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                print(
                    f"Response received from {model}",
                    flush=True
                )

                return response.text

            except Exception as e:

                error_message = str(e)

                print(
                    f"Attempt {attempt}/2 failed: {error_message}",
                    flush=True
                )

                # Retry only briefly
                if attempt < 2:

                    print(
                        "Retrying in 2 seconds...",
                        flush=True
                    )

                    time.sleep(2)

        print(
            f"Model {model} unavailable. Trying next model...",
            flush=True
        )

    return json.dumps({
        "root_cause": "Gemini API temporarily unavailable",
        "confidence": "Low",
        "evidence": evidence,
        "osi_layer": "Unknown",
        "next_command": "Retry diagnosis later",
        "fix_steps": [],
        "human_review": True
    })


if __name__ == "__main__":

    result = diagnose(
        "PC cannot reach the server",
        "PC-Switch-Server",
        """show interfaces status
Fa0/2 notconnect"""
    )

    print(
        "\n================ GEMINI DIAGNOSIS ================\n"
    )

    print(result)

    print(
        "\n===================================================="
    )