import json
from ai import chat
import tools.sum as sum_tool
import tools.generate_image as generate_image_tool
import tools.search as search_tool
import tools.scrape as scrape_tool

tool_modules = [sum_tool, generate_image_tool, search_tool, scrape_tool]
definitions = [tool.definition for tool in tool_modules]

history = []

def agent(input_text):
    history.append({"role": "user", "content": input_text})

    for _ in range(10):
        answer = chat(history, definitions)

        history.extend(answer["output"])

        if answer.get("message"):
            return answer["message"]

        execute(answer["calls"], history)

def execute(calls, history):
    for call in calls:
        tool = next((t for t in tool_modules if t.definition["name"] == call["name"]), None)
        if tool:
            args = json.loads(call["arguments"])
            print(args)
            result = tool.execute(args)
            print(result)
            history.append({
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(result)
            })