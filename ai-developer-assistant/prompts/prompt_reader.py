import os

PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_planner_prompt():
    with open(os.path.join(PROMPT_DIR, "planner_agent.md")) as file:
        return file.read()
