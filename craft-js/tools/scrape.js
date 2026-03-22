const BASE_URL = "https://api.firecrawl.dev/v2";

export const definition = {
  type: "function",
  name: "scrape_url",
  description:
    "Scrapes a single URL and returns its content as markdown",
  strict: false,
  parameters: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "The URL to scrape",
      },
    },
    required: ["url"],
    additionalProperties: false,
  },
};

export const execute = async ({ url }) => {
  const res = await fetch(`${BASE_URL}/scrape`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.FIRECRAWL_API_KEY}`,
    },
    body: JSON.stringify({
      url,
      formats: [{ type: "markdown" }],
    }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Firecrawl scrape error (${res.status}): ${error}`);
  }

  const { data } = await res.json();

  return {
    url: data?.metadata?.url ?? url,
    title: data?.metadata?.title ?? null,
    description: data?.metadata?.description ?? null,
    markdown: data?.markdown ?? null,
  };
};
