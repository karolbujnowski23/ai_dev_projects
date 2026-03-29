# Sensor Anomaly Detection (Task: Evaluation)

This project implements a modular, agentic solution to identify anomalies in a dataset of nearly 10,000 sensor readings. It validates technical data integrity and identifies logical inconsistencies between operator notes and system statuses.

## Project Structure

Based on a strict modular architecture:
- **`app.py`**: The main orchestrator that manages data loading, deduplication, LLM classification, and result submission.
- **`src/`**: Core logic files.
    - `config.py`: Configuration loader for API keys and model parameters.
    - `api.py`: Low-level clients for the Gemini Direct API and the Centrala verification endpoint.
    - `validators.py`: Quantitative validation logic for sensor ranges and active sensor types.
- **`logs/`**: Application runtime logs (`app.log`).
- **`prompt.md`**: The system instruction used by the LLM to detect semantic inconsistencies in operator notes.
- **`sensors/`**: Directory containing 9,999 JSON sensor files (0001.json - 9999.json).

## Anomaly Detection Logic

Anomalies are detected using a two-stage process:

1. **Technical Validation (Local)**:
    - Verifies that only sensors specified in `sensor_type` are reporting non-zero values.
    - Validates that active readings fall within predefined physical ranges (Temperature, Pressure, Water Level, Voltage, Humidity).
    - Identifies all "FAILED" sensors based on these quantitative metrics.

2. **Logical Inconsistency (LLM)**:
    - Extracts unique combinations of `sensor_type`, `readings`, and `operator_notes` from all technically "OK" files.
    - Uses `gemini-3.1-flash-lite-preview` to identify cases where an operator reports an error or anomaly despite the technical status being "OK".

## Optimization

To minimize LLM costs and context window usage:
- **Deduplication**: Instead of sending 10,000 files, the system identifies unique patterns.
- **Filtering**: Only technically "OK" files are sent to the LLM for semantic analysis; "FAILED" files are automatically included in the final recheck list.

## Setup & Usage

1. **Configure API Keys**: Ensure `zadania/.config` contains:
   - `APIKEY`: Your Centrala API key.
   - `GEMINI_LLM_APIKEY`: Your Google Gemini API key.

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Orchestrator**:
   ```bash
   python app.py
   ```

## Logging

All thoughts, API calls, and processing steps are logged to `logs/app.log` and the console for full observability.
