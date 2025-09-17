from openai import OpenAI

import json
import random
import uuid
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

adl_categories = ["Hydration", "Medication", "Hygiene", "Mobility", "Social Engagement"]
times_of_day = ["Morning", "Afternoon", "Evening"]
environments = ["Private room", "Dining area", "Bathroom", "Hallway", "Lounge"]
caregiver_roles = ["Personal Care Assistant", "Registered Nurse"]
resident_profiles = [
    "Female, 85, mild dementia, uses walker",
    "Male, 90, Parkinson’s, high fall risk",
    "Female, 79, moderate dementia, needs bathing assistance",
    "Male, 87, limited mobility, hearing impaired",
    "Female, 82, socially withdrawn, mild cognitive impairment"
]

def generate_prompt(adl, profile, time, env, role):
    return f"""
You are simulating a caregiver-resident interaction in an aged care setting. The scenario involves the ADL category: {adl}.

Resident profile:
- {profile}

Time of day: {time}
Environment: {env}
Caregiver role: {role}

Based on clinical guidelines for {adl.lower()}, generate a realistic dialogue between the caregiver and resident. Include 2–4 turns each. Annotate each utterance with:
- Speaker
- Intent
- Action

Also provide:
- Care goal
- Success criteria
- Risk flags (if any)

Return the output in structured JSON format.
"""

def generate_scenario():
    adl = random.choice(adl_categories)
    profile = random.choice(resident_profiles)
    time = random.choice(times_of_day)
    env = random.choice(environments)
    role = random.choice(caregiver_roles)

    prompt = generate_prompt(adl, profile, time, env, role)

    response = client.chat.completions.create(model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7)

    try:
        scenario_json = json.loads(response.choices[0].message.content)
        scenario_json["scenario_id"] = str(uuid.uuid4())
        return scenario_json
    except Exception as e:
        print("Error parsing response:", e)
        return None

# Generate 120 scenarios
scenarios = []
for _ in range(120):
    scenario = generate_scenario()
    if scenario:
        scenarios.append(scenario)

# Save to file
with open("synthetic_adl_scenarios_openai.json", "w") as f:
    json.dump(scenarios, f, indent=2)
