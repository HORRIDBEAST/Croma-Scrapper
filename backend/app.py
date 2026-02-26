from flask import Flask, jsonify
from flask_cors import CORS
import redis
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    logging.info("Successfully connected to Redis.")
except redis.ConnectionError as e:
    logging.error(f"Could not connect to Redis: {e}")
    r = None

@app.route("/products", methods=["GET"])
def get_products():
    """
    This endpoint returns the list of scraped product details.
    """
    if not r:
        return jsonify({"error": "Could not connect to Redis"}), 503

    try:
        product_data_json = r.get("croma_products")
        if product_data_json is None:
            return jsonify({"message": "No product data found. Please run the scraper first."}), 404
        
        products = json.loads(product_data_json)
        return jsonify(products)
    except Exception as e:
        logging.error(f"An error occurred in /products endpoint: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/scraped-content", methods=["GET"])
def get_scraped_content():
    """
    TODO: Complete this endpoint.
    This endpoint retrieves the scraped head and header content from Redis.
    """
    if not r:
        return jsonify({"error": "Could not connect to Redis"}), 503

    try:
        # Retrieve the page elements data from Redis
        page_elements_json = r.get("croma_page_elements")
        
        if page_elements_json is None:
            return jsonify({"message": "No page element data found. Please run the scraper first."}), 404
        
        # Parse the JSON string and return it
        data = json.loads(page_elements_json)
        return jsonify({"success": True, "data": data})
        
    except json.JSONDecodeError:
        return jsonify({"success": False, "message": "Failed to parse page element data from Redis."}), 500
    except Exception as e:
        logging.error(f"An error occurred in /scraped-content endpoint: {e}")
        return jsonify({"success": False, "message": f"An internal server error occurred: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint to confirm the backend is running."""
    return jsonify({"status": "healthy", "message": "Backend is running!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
