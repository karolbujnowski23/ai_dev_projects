def execute(args):
    return args["a"] + args["b"]

definition = {
    "type": "function",
    "name": "sum",
    "description": "Returns the sum of two numbers",
    "strict": False,
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["a", "b"],
        "additionalProperties": False,
    },
}