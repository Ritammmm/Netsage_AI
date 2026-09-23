import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def load_cases():

    path = os.path.join(
        "dataset",
        "cases.csv"
    )

    return pd.read_csv(path)


def get_case(data):

    while True:

        try:

            case_id = int(
                input("Enter Case ID (1-30): ")
            )

            case = data[
                data["Case_ID"] == case_id
            ]

            if len(case) == 0:

                print(
                    "Case not found. Enter a number from 1 to 30."
                )

                continue

            return case.iloc[0]

        except ValueError:

            print(
                "Please enter a valid number."
            )


def create_prompt(case):

    return f"""
You are NetSage AI, a Cisco network troubleshooting assistant.

Analyze the following troubleshooting case.

SYMPTOM:
{case['Symptom']}

TOPOLOGY:
{case['Topology_Note']}

SHOW COMMAND EVIDENCE:
{case['Show_Output_Evidence']}

EXPECTED FAULT:
{case['Expected_Fault']}

CONCEPT:
{case['Concept_Tag']}

SEVERITY:
{case['Severity']}

Return ONLY valid JSON.

Required fields:

root_cause
confidence
evidence
osi_layer
next_command
fix_steps
human_review

Rules:

1. Use the supplied evidence.
2. Do not invent show-command output.
3. If evidence is insufficient, say so.
4. Never apply a configuration change automatically.
5. Human approval is mandatory.
6. The evidence must support the diagnosis.
"""


def clean_json_response(text):

    text = text.strip()

    if text.startswith("```json"):

        text = text[
            len("```json"):
        ]

    elif text.startswith("```"):

        text = text[
            len("```"):
        ]

    if text.endswith("```"):

        text = text[
            :-len("```")
        ]

    return text.strip()


def get_ai_diagnosis(case):

    prompt = create_prompt(case)

    models_to_try = [
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.6-flash"
    ]

    for model_name in models_to_try:

        for attempt in range(3):

            try:

                print(
                    f"Trying {model_name} "
                    f"(attempt {attempt + 1}/3)..."
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                text = clean_json_response(
                    response.text
                )

                try:

                    result = json.loads(text)

                    return result

                except json.JSONDecodeError:

                    print(
                        "Gemini returned text that "
                        "was not valid JSON."
                    )

                    return {
                        "root_cause": "Unable to parse AI response",
                        "confidence": "N/A",
                        "evidence": response.text,
                        "osi_layer": "Unknown",
                        "next_command": "Review the AI response manually",
                        "fix_steps": [
                            "Inspect the raw AI response",
                            "Collect additional network evidence"
                        ],
                        "human_review": True
                    }

            except Exception as error:

                error_text = str(error)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text
                ):

                    print(
                        "Gemini is temporarily busy."
                    )

                    if attempt < 2:

                        wait_time = 5 * (
                            2 ** attempt
                        )

                        print(
                            f"Waiting {wait_time} seconds..."
                        )

                        time.sleep(
                            wait_time
                        )

                    else:

                        print(
                            f"{model_name} failed "
                            "after 3 attempts."
                        )

                else:

                    print(
                        "\nGemini API error:"
                    )

                    print(error)

                    break

    print(
        "\nAll Gemini models are currently "
        "unavailable."
    )

    return {
        "root_cause": "AI service temporarily unavailable",
        "confidence": "N/A",
        "evidence": (
            "Gemini API returned a temporary "
            "service availability error."
        ),
        "osi_layer": "Not determined",
        "next_command": "Retry the AI diagnosis",
        "fix_steps": [
            "Wait and retry the Gemini request",
            "Use the deterministic rule checker",
            "Do not apply a configuration change automatically"
        ],
        "human_review": True
    }


def run_rule_checks(case):

    evidence = str(
        case["Show_Output_Evidence"]
    ).lower()

    findings = []

    if "notconnect" in evidence:

        findings.append(
            "Interface or physical link may be down"
        )

    if "down" in evidence:

        findings.append(
            "Interface status indicates a possible down interface"
        )

    if "vlan" in evidence:

        findings.append(
            "VLAN configuration should be verified"
        )

    if "route" in evidence:

        findings.append(
            "Routing table should be verified"
        )

    if "gateway" in evidence:

        findings.append(
            "Default gateway should be verified"
        )

    if "nat" in evidence:

        findings.append(
            "NAT configuration should be verified"
        )

    if "acl" in evidence:

        findings.append(
            "ACL configuration should be verified"
        )

    if len(findings) == 0:

        findings.append(
            "No deterministic rule matched this evidence"
        )

    return findings


def display_case(case):

    print("\n" + "=" * 60)

    print(
        "NETSAGE AI TROUBLESHOOTING CASE"
    )

    print("=" * 60)

    print("\nCase ID:")
    print(case["Case_ID"])

    print("\nSymptom:")
    print(case["Symptom"])

    print("\nTopology:")
    print(case["Topology_Note"])

    print("\nEvidence:")
    print(case["Show_Output_Evidence"])

    print("\nExpected Fault:")
    print(case["Expected_Fault"])

    print("\nConcept:")
    print(case["Concept_Tag"])

    print("\nSeverity:")
    print(case["Severity"])


def display_ai_result(result):

    print("\n" + "=" * 60)

    print(
        "GEMINI AI DIAGNOSIS"
    )

    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=4
        )
    )


def display_rules(findings):

    print("\n" + "=" * 60)

    print(
        "RULE CHECKER FINDINGS"
    )

    print("=" * 60)

    for finding in findings:

        print(
            "- " + finding
        )


def human_review(
    case,
    ai_result,
    findings
):

    print("\n" + "=" * 60)

    print(
        "HUMAN REVIEW"
    )

    print("=" * 60)

    print("\nChoose one:")

    print("A = Accepted")
    print("E = Edited")
    print("R = Rejected")

    while True:

        choice = input(
            "\nYour decision: "
        ).strip().upper()

        if choice in [
            "A",
            "E",
            "R"
        ]:

            break

        print(
            "Please enter A, E, or R."
        )

    if choice == "A":

        status = "Accepted"

        comment = input(
            "Optional review comment: "
        )

    elif choice == "E":

        status = "Edited"

        comment = input(
            "Explain what you corrected: "
        )

    else:

        status = "Rejected"

        comment = input(
            "Explain why the diagnosis was rejected: "
        )

    log_review(
        case,
        ai_result,
        findings,
        status,
        comment
    )

    print(
        "\nHuman review saved."
    )


def log_review(
    case,
    ai_result,
    findings,
    status,
    comment
):

    os.makedirs(
        "logs",
        exist_ok=True
    )

    log_file = os.path.join(
        "logs",
        "human_review.csv"
    )

    row = {

        "Case_ID":
            case["Case_ID"],

        "Symptom":
            case["Symptom"],

        "AI_Root_Cause":
            ai_result.get(
                "root_cause",
                "N/A"
            ),

        "AI_Confidence":
            ai_result.get(
                "confidence",
                "N/A"
            ),

        "AI_OSI_Layer":
            ai_result.get(
                "osi_layer",
                "N/A"
            ),

        "AI_Next_Command":
            ai_result.get(
                "next_command",
                "N/A"
            ),

        "Rule_Findings":
            "; ".join(
                findings
            ),

        "Human_Decision":
            status,

        "Human_Comment":
            comment
    }

    new_data = pd.DataFrame(
        [row]
    )

    if os.path.exists(log_file):

        new_data.to_csv(
            log_file,
            mode="a",
            header=False,
            index=False
        )

    else:

        new_data.to_csv(
            log_file,
            index=False
        )


def main():

    print("\n" + "=" * 60)

    print(
        "NETSAGE AI"
    )

    print(
        "AI-Assisted Network Troubleshooting"
    )

    print(
        "Human Review Required"
    )

    print("=" * 60)

    data = load_cases()

    case = get_case(
        data
    )

    display_case(
        case
    )

    print(
        "\nRunning Gemini diagnosis..."
    )

    ai_result = get_ai_diagnosis(
        case
    )

    display_ai_result(
        ai_result
    )

    print(
        "\nRunning deterministic rule checks..."
    )

    findings = run_rule_checks(
        case
    )

    display_rules(
        findings
    )

    human_review(
        case,
        ai_result,
        findings
    )


if __name__ == "__main__":

    main()