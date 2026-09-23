from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_engine.diagnosis import diagnose
from checker.rule_checker import run_rule_checks

import json
import re


app = FastAPI(title="NetSage AI API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": "NetSage AI backend is running"
    }


def parse_ai_response(result):

    result = result.strip()

    # Remove Markdown code fences
    result = re.sub(
        r"^```json\s*",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"^```\s*",
        "",
        result
    )

    result = re.sub(
        r"\s*```$",
        "",
        result
    )

    result = result.strip()

    # First attempt: direct JSON parsing
    try:

        return json.loads(result)

    except json.JSONDecodeError:
        pass


    # Second attempt:
    # Find the JSON object inside additional text

    start = result.find("{")
    end = result.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_part = result[start:end + 1]

        try:

            return json.loads(json_part)

        except json.JSONDecodeError:
            pass


    # If parsing completely fails,
    # return a safe structured response

    return {
        "root_cause": result,
        "confidence": "Unknown",
        "evidence": [],
        "osi_layer": "Unknown",
        "next_command": "",
        "fix_steps": [],
        "human_review": True
    }


@app.post("/diagnose")
def run_diagnosis(data: dict):

    symptom = data.get("symptom", "")
    topology = data.get("topology", "")
    command_output = data.get("command_output", "")


    # -------------------------------------------------
    # AI DIAGNOSIS
    # -------------------------------------------------

    result = diagnose(
        symptom,
        topology,
        command_output
    )


    diagnosis = parse_ai_response(result)


    # -------------------------------------------------
    # DETERMINISTIC RULE CHECKER
    # -------------------------------------------------

    rule_findings = run_rule_checks(
        symptom,
        topology,
        command_output
    )


    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------

    return {
        "diagnosis": diagnosis,
        "rule_checker": rule_findings
    }