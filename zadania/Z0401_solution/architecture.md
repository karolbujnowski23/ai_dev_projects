# Architecture of the Z0401 OKO Editor Solver

This document outlines the architecture of the Python-based solution for the "okoeditor" task (Z0401). The system is designed to be modular, robust, and follows the structure defined in the `advanced-python-solver` skill.

## 1. System Components

The application is broken down into several key components, each with a specific responsibility.

### `app.py` - The Orchestrator
- **Purpose**: This is the main entry point of the application. It controls the overall flow of the solution.
- **Responsibilities**:
    1.  Initializes the logging configuration.
    2.  Calls the scraper to fetch dynamic data (IDs) from the OKO web panel.
    3.  Executes the required sequence of actions as defined in `Z0401text.md`.
    4.  Builds the JSON payloads for each action.
    5.  Uses the `api.py` module to send each payload to the central hub.
    6.  Logs the outcome of each step.
    7.  Sends the final "done" action to verify the task's completion.

### `src/config.py` - Configuration Management
- **Purpose**: Centralizes all configuration variables.
- **Responsibilities**:
    1.  Uses `python-dotenv` to load environment variables from a `.config` file located in the parent `zadania` directory.
    2.  Exposes variables like `APIKEY`, `CENTRALA_URL`, and `OKO_URL` for other modules to use.
    3.  Keeps sensitive information out of the source code.

### `src/scraper.py` - Web Scraper
- **Purpose**: To dynamically fetch required information from the OKO web panel that is not available via the API.
- **Responsibilities**:
    1.  Uses `playwright` to handle the login process, as the site is likely JavaScript-rendered.
    2.  Navigates to the "incydenty" and "zadania" pages.
    3.  Parses the HTML content using `BeautifulSoup4` to find the specific hexadecimal IDs for the Skolwin incident and task.
    4.  Returns these IDs to the orchestrator. This makes the solution resilient to changes in the data on the website.

### `src/api.py` - API Client
- **Purpose**: To handle all communication with the external `hub.ag3nts.org` API.
- **Responsibilities**:
    1.  Provides a clean function (`send_to_centrala`) for sending JSON payloads.
    2.  Constructs the full request body, including the `apikey` and `task` name.
    3.  Handles HTTP requests using the `requests` library.
    4.  Includes robust error handling and logging for API requests, printing status codes and response bodies on failure.

### `logs/app.log` - Logging
- **Purpose**: To provide a persistent record of the application's execution.
- **Responsibilities**:
    1.  The `logging` module is configured in `app.py` to write timestamped logs to this file.
    2.  Captures key events, such as scraping results, payloads being sent, and API responses received. This is crucial for debugging and verifying the agent's actions.

## 2. Data Flow

The data flows through the system in a linear sequence:

1.  `app.py` starts and calls `get_skolwin_ids()` from `src/scraper.py`.
2.  The scraper logs into `oko.ag3nts.org`, scrapes the necessary pages, and returns the dynamic IDs.
3.  `app.py` receives the IDs and proceeds to build the first JSON payload (to modify the Skolwin incident).
4.  The payload is passed to `send_to_centrala()` in `src/api.py`.
5.  `src/api.py` sends the request to `hub.ag3nts.org/verify` and returns the JSON response.
6.  `app.py` logs the response and repeats steps 3-5 for the remaining tasks (updating the task, creating the Komarowo incident).
7.  Finally, `app.py` sends the `{"action": "done"}` payload to finalize the task.

This modular design ensures that each part of the system has a single responsibility, making the code easier to understand, maintain, and debug.
