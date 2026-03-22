# Craft Python Agent

This is a Python translation of an AI Agent project that uses OpenAI's GPT-4o model to intelligently execute tools based on user prompts. 

The agent runs an evaluation loop to determine which tool to call, executes it, and feeds the results back to the model until it can fulfill the user's request.

## Available Tools
- **sum**: Returns the sum of two numbers.
- **web_search**: Searches the web for a given query and returns results with markdown content (Powered by Firecrawl).
- **scrape_url**: Scrapes a single URL and returns its content as markdown (Powered by Firecrawl).
- **generate_image**: Generates an image from a text prompt and saves it to disk (Powered by Gemini 3.1 Flash Image Preview).

## Prerequisites
- Python 3.8+
- [OpenAI API Key](https://platform.openai.com/)
- [Gemini API Key](https://aistudio.google.com/)
- [Firecrawl API Key](https://www.firecrawl.dev/)

## Installation

1. Navigate to the project directory:
   ```bash
   cd craft-python
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```
   *(On Windows Command Prompt, use `copy env.example .env`)*

2. Open the `.env` file and fill in your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

## Usage

Run the main application:
```bash
python app.py
```

By default, it will run the agent with the prompt: *"Write up the specs for the AirPods Max 2, which were released yesterday."* You can change the prompt inside `app.py`. Any generated images will be saved in an `output/` directory.