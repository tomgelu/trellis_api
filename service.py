from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
from process import process_image
from initialize import initialize_models
import uuid
import logging
import threading
import time
from job_manager import JobManager, JobStatus
from urllib.parse import urljoin
import atexit

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = os.getenv('TRELLIS_INPUT_DIR', "/workspace/TRELLIS/input")
OUTPUT_DIR = os.getenv('TRELLIS_OUTPUT_DIR', "/workspace/TRELLIS/output")
BASE_URL = os.getenv('TRELLIS_BASE_URL', 'http://localhost:5000')

# Initialize job manager
job_manager = JobManager()

# Add at the top with other globals
initialization_lock = threading.Lock()
is_initialized = False

@app.route('/output/<request_id>/<filename>')
@cross_origin()
def serve_file(request_id, filename):
    """Serve files from the output directory"""
    return send_from_directory(os.path.join(OUTPUT_DIR, request_id), filename)

@app.route('/initialize', methods=['POST'])
@cross_origin()
def initialize():
    global is_initialized
    app.logger.info("Received initialization request")   
    
    request_id = str(uuid.uuid4())
    
    with initialization_lock:
        if is_initialized:
            return jsonify({
                'status': 'success',
                'message': 'Already initialized',
                'request_id': request_id
            })
            
        try:
            app.logger.info("Starting initialization process")
            initialize_models()
            is_initialized = True

            result = {
                'status': 'success',
                'request_id': request_id,
            }
            app.logger.info(f"Initialization complete: {result}")
            return jsonify(result)
        except Exception as e:
            app.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 500

@app.route('/status/<request_id>', methods=['GET'])
@cross_origin()
def get_status(request_id):
    job = job_manager.get_job(request_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    response = {
        'status': job.status.value,
        'processing_time': time.time() - job.start_time
    }
    
    if job.status == JobStatus.COMPLETED:
        response['result'] = job.result
    elif job.status == JobStatus.FAILED:
        response['error'] = job.error
        
    return jsonify(response)

@app.route('/process', methods=['POST'])
@cross_origin()
def process():
    global is_initialized
    app.logger.info("Received process request")
    
    if not is_initialized:
        return jsonify({
            'error': 'Service not initialized. Please call /initialize first'
        }), 400
        
    request_id = str(uuid.uuid4())
    job = job_manager.create_job(request_id)
    
    # Create output directory
    request_output_dir = os.path.join(OUTPUT_DIR, request_id)
    os.makedirs(request_output_dir, exist_ok=True)
    
    # Handle file upload
    if 'image' in request.files:
        file = request.files['image']
        input_path = os.path.join(INPUT_DIR, f"{request_id}.webp")
        file.save(input_path)
    elif 'image' in request.form:
        input_path = request.form['image']
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 400
    else:
        return jsonify({'error': 'No image provided'}), 400
    
    # Start processing in background thread
    thread = threading.Thread(
        target=run_processing,
        args=(request_id, input_path, request_output_dir)
    )
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'request_id': request_id
    })

def run_processing(request_id, input_path, output_dir):
    job = job_manager.get_job(request_id)
    job.status = JobStatus.PROCESSING
    
    try:
        result = process_image(input_path, output_dir)
        job.status = JobStatus.COMPLETED
        job.result = {
            'output_files': result,
            'base_url': urljoin(BASE_URL, f'/output/{request_id}')
        }
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)
        app.logger.error(f"Processing failed: {str(e)}", exc_info=True)
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

def cleanup():
    """Cleanup resources on shutdown"""
    app.logger.info("Cleaning up resources...")
    # Add any cleanup needed for the pipeline
    global _pipeline
    if _pipeline:
        del _pipeline
    
atexit.register(cleanup)

@app.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    return jsonify({
        'status': 'healthy',
        'initialized': is_initialized,
        'active_jobs': len(job_manager.jobs)
    })

if __name__ == '__main__':
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting TRELLIS service on port 5000...")
    # Increase timeout and enable debug mode
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)