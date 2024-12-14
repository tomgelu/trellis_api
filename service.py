from flask import Flask, request, jsonify
import os
from process import process_image
from initialize import initialize_models
import uuid
import logging


app = Flask(__name__)
# Set up logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = "/workspace/TRELLIS/input"
OUTPUT_DIR = "/workspace/TRELLIS/output"

@app.route('/initialize', methods=['POST'])
def initialize():
    app.logger.info("Received request")   
    
    request_id = str(uuid.uuid4())
    
    try:
        app.logger.info("Starting initialization process")
        # Process the image
        initialize_models()

        result = {
            'status': 'success',
            'request_id': request_id,
        }
        app.logger.info(f"Initialization complete: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process():
    app.logger.info("Received request")
    if 'image' not in request.files:
        app.logger.error("No image in request")
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    app.logger.info(f"Received file: {file.filename}")
    
    if file.filename == '':
        app.logger.error("Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    
    # Create unique ID for this request
    request_id = str(uuid.uuid4())
    request_output_dir = os.path.join(OUTPUT_DIR, request_id)
    os.makedirs(request_output_dir, exist_ok=True)
    app.logger.info(f"Created output directory: {request_output_dir}")
    
    # Save uploaded file
    input_path = os.path.join(INPUT_DIR, f"{request_id}.webp")
    app.logger.info(f"Saving file to: {input_path}")
    file.save(input_path)
    
    try:
        app.logger.info("Starting image processing")
        # Process the image
        output_files = process_image(input_path, request_output_dir)
        
        result = {
            'status': 'success',
            'request_id': request_id,
            'output_files': output_files
        }
        app.logger.info(f"Processing complete: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
            app.logger.info(f"Cleaned up input file: {input_path}")
            
if __name__ == '__main__':
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting TRELLIS service on port 5000...")
    # Increase timeout and enable debug mode
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)