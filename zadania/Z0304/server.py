from flask import Flask, request, jsonify
from src.helpers.logger import log
from src.data_processor import load_data, find_cities_with_all_items
from src.api import extract_items_with_llm
from src.config import SERVER_PORT

app = Flask(__name__)

# Load data at startup
log.info("Loading initial data...")
cities_df, items_df, connections_df = load_data()

@app.route('/api/negotiations', methods=['POST'])
def negotiations():
    """
    Endpoint for the centrala agent. It parses natural language to find cities
    that contain all requested items.
    """
    try:
        data = request.get_json()
        if not data or 'params' not in data:
            return jsonify({"error": "Missing 'params' in request"}), 400

        query = data['params']
        log.info(f"Received query: {query}")

        # Extract item names using the LLM to handle Polish inflections
        available_items = items_df['name'].str.lower().unique().tolist()
        item_list = extract_items_with_llm(query, available_items)
        log.info(f"Extracted items: {item_list}")

        if not item_list:
            log.info("No items identified in the query.")
            return jsonify({"output": "I could not identify any valid items in your request. Please specify the exact names of the items you need."})

        # Find cities matching all extracted items
        cities = find_cities_with_all_items(item_list, items_df, cities_df, connections_df)
        log.info(f"Cities found: {cities}")

        # Format the response
        response_text = ", ".join(cities) if cities else "No city offers all the requested items."
        
        # Enforce technical limitations (4 to 500 bytes)
        if len(response_text.encode('utf-8')) > 500:
            log.info("Response exceeded 500 bytes.")
            response_text = "The response is too large. Please refine your query to narrow down the items."
        if len(response_text.encode('utf-8')) < 4:
            log.info("Response below 4 bytes.")
            response_text = "No results found matching your query."

        return jsonify({"output": response_text})

    except Exception as e:
        log.error(f"An internal server error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Start the server (usually on your hosting environment, you use gunicorn/waitress instead of app.run)
    # app.run(debug=True, host='0.0.0.0', port=5000)
    log.info(f"Starting server on port {SERVER_PORT}...")
    app.run(debug=False, host='0.0.0.0', port=SERVER_PORT)