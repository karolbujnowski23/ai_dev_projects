# DRN-BMB7 Drone Mission Agent

This project implements an autonomous AI agent to control the DRN-BMB7 drone, completing the objective of identifying and targeting a dam near the Żarnowiec power plant to restore cooling systems.

## Project Structure

```
Z0205/
├── app.py             # Main application orchestrator (Vision -> Agent -> Verification)
├── src/               # Application core logic
│   ├── api.py         # Gemini API client with retry mechanism (exponential backoff)
│   ├── config.py      # Environment variables configuration and validation
│   ├── logger.py      # Centralized logging configuration (writes to logs/app.log)
│   └── tools.py       # Drone API integration and verification endpoint handler
├── logs/              # Directory for log files (created automatically)
│   └── app.log        # Detailed execution logs (Vision, Agent steps, API responses)
├── drone_manual.md    # Documentation of the drone's API used as context for the agent
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## How It Works

1.  **Vision Phase (`gemini-3-flash-preview`)**: The application downloads the map of the power plant area. The vision model analyzes the map grid to locate the sector containing the "intense blue water" (the dam) and estimates the coordinates (x, y).
2.  **Instruction Generation (`gemini-2.5-flash`)**: The vision analysis results, mission parameters (altitude 100m, target ID `PWR6132PL`), and the `drone_manual.md` are passed to the agent model. The agent generates a JSON array of commands for the drone.
3.  **Reactive Loop (Verification & Correction)**: The generated instructions are sent to the central Hub API (`/verify`).
    *   If successful, the mission completes, and the flag `{FLG:...}` is retrieved.
    *   If the drone API returns an error (e.g., missing calibration, wrong parameter order), the error message is fed back to the agent. The agent analyzes the error against the manual, corrects the JSON sequence, and tries again.
    *   This loop continues until success or the maximum number of attempts is reached.

## Setup

1.  **Environment Variables**: Ensure you have a `.config` file two directories above this project (`../../.config`) containing the following keys:
    *   `APIKEY`: Your personal identification key for the Hub API.
    *   `GEMINI_LLM_APIKEY`: Your Google Gemini API key.
2.  **Dependencies**: Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main orchestrator script:

```bash
python app.py
```

Check the console output for the final result, or review `logs/app.log` for a detailed breakdown of the AI's reasoning, API payloads, and responses.