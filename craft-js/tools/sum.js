export const definition = {
    type: "function",
    name: "sum",
    description: "Returns the sum of two numbers",
    strict: false,
    parameters: {
      type: "object",
      properties: {
        a: { type: "number" },
        b: { type: "number" },
      },
      required: ["a", "b"],
      additionalProperties: false,
    },
  };
  
  export const execute = ({ a, b }) => a + b;