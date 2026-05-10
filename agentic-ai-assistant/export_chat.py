# =========================
# EXPORT FUNCTIONS
# =========================

import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage                    
                                                                                                
def _role(msg):
    if isinstance(msg, HumanMessage): return "user"                                           
    if isinstance(msg, AIMessage):    return "assistant"                                      
    if isinstance(msg, SystemMessage):return "system"
    return "unknown"                                                                          
                                                                                            
def export_as_txt(messages):
    return "".join(f"{_role(m).upper()}:\n{m.content}\n\n" for m in messages)                 
                                                                                            
def export_as_markdown(messages):
    return "".join(f"## {_role(m).upper()}\n\n{m.content}\n\n" for m in messages)             
                                                                                            
def export_as_json(messages):
    return json.dumps(                                                                        
        [{"role": _role(m), "content": m.content} for m in messages],
        indent=4, ensure_ascii=False,                                                         
      )