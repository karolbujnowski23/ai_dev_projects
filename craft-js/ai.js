async function chat(input, tools) {
  const res = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({ model: "gpt-4o", input, tools }),
  });

  const data = await res.json();
  
  const message = data.output.find((o) => o.type === "message");
  const calls = data.output.filter((o) => o.type === "function_call");

  return {
    message: message?.content[0].text,
    calls,
    output: data.output,
  };
}

export { chat };