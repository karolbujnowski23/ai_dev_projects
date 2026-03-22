import { writeFileSync, mkdirSync } from "fs";
import { resolve } from "path";

const OUTPUT_DIR = resolve("output");

export const definition = {
  type: "function",
  name: "generate_image",
  description:
    "Generates an image from a text prompt using Gemini Nano Banana 2 and saves it to disk",
  strict: false,
  parameters: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "Text description of the image to generate",
      },
    },
    required: ["prompt"],
    additionalProperties: false,
  },
};

export const execute = async ({ prompt }) => {
  mkdirSync(OUTPUT_DIR, { recursive: true });

  const res = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/interactions",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": process.env.GEMINI_API_KEY,
      },
      body: JSON.stringify({
        model: "gemini-3.1-flash-image-preview",
        input: prompt,
        response_modalities: ["IMAGE"],
      }),
    }
  );

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Gemini API error (${res.status}): ${error}`);
  }

  const data = await res.json();
  const image = data.outputs?.find((o) => o.type === "image");

  if (!image) {
    throw new Error("No image returned from Gemini API");
  }

  const filename = `image_${Date.now()}.png`;
  const filepath = resolve(OUTPUT_DIR, filename);
  writeFileSync(filepath, Buffer.from(image.data, "base64"));

  return { filepath, filename };
};
