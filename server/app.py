from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import logging
import datetime
from routes.upload import upload_bp
from processing import get_job_status, processing_jobs

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts-server')

app = Flask(__name__)
CORS(app)

# Register upload blueprint
app.register_blueprint(upload_bp)

# Serve static files from shorts_output
@app.route('/shorts_output/<path:filename>')
def serve_output_file(filename):
    """Serve files directly from the shorts_output directory"""
    directory = os.path.abspath("shorts_output")
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        # List directory contents to help debug
        try:
            dir_contents = os.listdir(directory)
            logger.info(f"Directory contents: {dir_contents}")
        except Exception as e:
            logger.error(f"Could not list directory: {str(e)}")
        return jsonify({"error": "File not found"}), 404
    
    # Log file details
    logger.info(f"Serving file: {file_path}, size: {os.path.getsize(file_path)} bytes")
    
    # Determine content type based on file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension == '.mp4':
        mime_type = 'video/mp4'
    elif file_extension in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    else:
        mime_type = 'application/octet-stream'
    
    # Serve the file
    return send_file(file_path, mimetype=mime_type)

# Job status endpoint
@app.route('/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get the status of a processing job"""
    status = get_job_status(job_id)
    return jsonify(status)

# API test endpoint
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple endpoint to verify the API is running"""
    logger.info("Test API endpoint called")
    return jsonify({
        "status": "success", 
        "message": "API is running on port 5050",
        "timestamp": str(datetime.datetime.now())
    })

if __name__ == "__main__":
    # Make sure the output directory exists
    os.makedirs("shorts_output", exist_ok=True)
    
    # Run the server
    logger.info("Starting Flask server on port 5050")
    app.run(debug=True, host='0.0.0.0', port=5050)
