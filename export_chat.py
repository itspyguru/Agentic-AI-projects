# =========================
# EXPORT FUNCTIONS
# =========================

import json

def export_as_txt(messages):
    content = ""
    for message in messages:
        role = message["role"].upper()
        content += f"{role}:\n{message['content']}\n\n"
    return content

def export_as_json(messages):
    return json.dumps(messages, indent=4, ensure_ascii=False)

def export_as_markdown(messages):
    content = ""
    for message in messages:
        role = message["role"].upper()
        content += f"## {role}\n\n{message['content']}\n\n"
    return content