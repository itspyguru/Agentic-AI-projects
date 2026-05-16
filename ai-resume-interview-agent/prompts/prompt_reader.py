import os

PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_ats_prompt():
    with open(os.path.join(PROMPTS_DIR, "ats_prompt.md")) as file:
        return file.read()