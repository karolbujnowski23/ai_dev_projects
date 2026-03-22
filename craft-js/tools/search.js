const BASE_URL = "https://api.firecrawl.dev/v2";

export const definition = {
  type: "function",
  name: "web_search",
  description:
    "Searches the web for a given query and returns results with markdown content",
  strict: false,
  parameters: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "The search query (supports operators like site:, filetype:, intitle:)",
      },
      limit: {
        type: "number",
        description: "Maximum number of results to return (1-100, default 5)",
      },
    },
    required: ["query"],
    additionalProperties: false,
  },
};

export const execute = async ({ query, limit = 5 }) => {
  const res = await fetch(`${BASE_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.FIRECRAWL_API_KEY}`,
    },
    body: JSON.stringify({
      query,
      limit,
      scrapeOptions: {
        formats: [{ type: "markdown" }],
      },
    }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Firecrawl search error (${res.status}): ${error}`);
  }

  const { data } = await res.json();

  return (data?.web ?? []).map(({ title, url, description, markdown }) => ({
    title,
    url,
    description,
    markdown: markdown ?? null,
  }));
};
