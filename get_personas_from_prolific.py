import argparse
import pandas as pd
import json
from typing import Dict, List

def read_jsonl(filepath: str) -> List[Dict]:
    """Read JSONL file and return list of dictionaries."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def generate_persona_from_prolific(person: Dict) -> str:
    """Generate natural language directions (for judge) and third-person descriptions (for consultant/debater) from Prolific data."""

    # Second-person instructions
    directions = f"You are a {person['What is your age range?']} year old {person['Gender : How do you identify ?'].lower()} who grew up in a {person['What best describes your place of residence ?'].lower()} area. "
    directions += f"Your political stance is {person['What is your political stance?'].lower()}. "
    directions += f"Your household income level is {person['What is your personal income per year (in USD) ?']}. "
    directions += f"You identify your ethnicity as {person['What racial or ethnic groups describe you ?']}. "
    directions += f"Your primary language is {person['Primary language']}. "
    directions += f"Your education level is {person['What is your highest level of education?']}. "
    directions += f"Your religious belief is {person['Please state your religion.  ']}. "
    
    directions += f"\n\nYour beliefs about COVID-19 are as follows:\n"


    # Third person
    desc = f"The judge is a {person['What is your age range?']} year old {person['Gender : How do you identify ?'].lower()} who grew up in a {person['What best describes your place of residence ?'].lower()} area. "
    if person['Gender : How do you identify ?'].lower() == "female":
        pronoun = ("She", "Her")
        verb = "identifies"
    elif person['Gender : How do you identify ?'].lower() == "male":
        pronoun = ("He", "His")
        verb = "identifies"
    else:
        pronoun = ("They", "Their")
        verb = "identify"
    desc += f"{pronoun[1]} political stance is {person['What is your political stance?'].lower()}. "
    desc += f"{pronoun[1]} household income level is {person['What is your personal income per year (in USD) ?']}. "
    desc += f"{pronoun[0]} {verb} {pronoun[1].lower()} ethnicity as {person['What racial or ethnic groups describe you ?']}. "
    desc += f"{pronoun[1]} primary language is {person['Primary language']}. "
    desc += f"{pronoun[1]} education level is {person['What is your highest level of education?']}. "
    desc += f"{pronoun[1]} religious belief is {person['Please state your religion.  ']}. "
    
    desc += f"\n\n{pronoun[1]} beliefs about COVID-19 are as follows:\n"

    
    covid_questions = [
        "Do you think COVID-19 was a man-made virus ? ",
        "Do you think COVID-19 vaccines are safe and effective?",
        "Do you think masks provide real protection against COVID-19?",
        "Do you think stay-at-home measures helped prevent COVID-19 spread?",
        "Do you believe children face the same level of risk from COVID-19 as adults? ",
        "Do you think asymptomatic individuals can transmit COVID-19? ",
        "Do you believe hydroxychloroquine is an effective treatment for COVID-19? ",
        "Do you think certain blood types make people more susceptible to COVID-19? ",
        "Do you believe convalescent plasma therapy improves outcomes for COVID-19 patients? ",
        "Do you think COVID-19 can cause long-term neurological effects? ",
        "Scientists say children are at lower risk from COVID-19 than adults. Do you believe this is true?",
        "Do you believe natural immunity from infection offers better protection than vaccination?",
        "Do you believe plasma from recovered patients helps treat severe COVID-19?",

        # batch 2
        "Which statement best represents your view on COVID-19?",
    ]
    for question in covid_questions:
        if question in person and isinstance(person[question], str):
            directions += "Q: " + question + "\n"
            directions += "A: " + person[question] + "\n"
            directions += "\n"

            desc += "Q: " + question + "\n"
            desc += "A: " + person[question] + "\n"
            desc += "\n"

    return {
        "directions": directions,
        "description": desc
    }

def process_prolific_data(input_file: str, output_file: str):
    """Read Prolific data and write formatted personas to file."""
    personas = []
    for i in input_file:
        # Read JSONL data
        personas.append(pd.read_csv(i))

    # Process each persona and write to output file
    with open(output_file, 'w') as f:
        output_data = {}
        for p in personas:
            for idx, person in p.iterrows():
                submission_id = person["Participant id"]
                output_data[submission_id] = generate_persona_from_prolific(person)

        # Write the complete data as JSON line
        f.write(json.dumps(output_data, indent=4) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", "-i", action='append', type=str, required=True)
    parser.add_argument("--output-file", "-o", action='store', default='./personas/all_personas.json', type=str)
    args = parser.parse_args()
    process_prolific_data(args.input_file, args.output_file)
