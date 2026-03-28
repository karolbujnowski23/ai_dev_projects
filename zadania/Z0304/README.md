# Deployment Instructions

## Server Details
- **Server:** `frog02.mikr.us`
- **SSH Port:** `10451`

## Steps
1.  **Connect to the server:**
    ```bash
    ssh your_username@frog02.mikr.us -p 10451
    ```
2.  **Navigate to the deployment directory and copy files:**
    Create a directory for the project on the server. Then, use `scp` to copy your local `zadania/Z0304/` directory to the server.
    ```bash
    scp -P 10451 -r /path/to/your/local/zadania/Z0304 your_username@frog02.mikr.us:/path/to/deployment/directory
    ```
3.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the application:**
    For development, you can run the app directly. Make sure to bind it to `0.0.0.0` to make it accessible.
    ```bash
    flask --app app run --host=0.0.0.0 --port=YOUR_CHOSEN_PORT
    ```
    Replace `YOUR_CHOSEN_PORT` with a free port on the server. Your public URL will be `http://frog02.mikr.us:YOUR_CHOSEN_PORT/api/negotiations`.
