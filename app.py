from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from profanity_filter import ProfanityFilter
from image import ImageProfanityChecker
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

print("Initializing profanity filter...")
profanity_filter = ProfanityFilter(model_path="Anvesh18/zeroshot-profanity-filter", threshold=0.5)
print("Profanity filter ready!")

print("Initializing image profanity checker...")
image_checker = ImageProfanityChecker()
print("Image profanity checker ready!")


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check_profanity():
    """
    Check if text contains profanity without censoring.
    
    Request body:
        {
            "text": "Text to check"
        }
    
    Response:
        {
            "is_profane": bool,
            "profane_probability": float,
            "non_profane_probability": float,
            "label": str,
            "text": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        
        if not text or not text.strip():
            return jsonify({
                'error': 'Text cannot be empty'
            }), 400
        
        result = profanity_filter.is_profane(text)
        result['text'] = text
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/filter', methods=['POST'])
def filter_text():
    """
    Filter text for profanity and return censored version.
    
    Request body:
        {
            "text": "Text to filter",
            "mode": "full" | "word" | "aggressive" (optional, default: "full"),
            "threshold": float (optional, default: 0.5)
        }
    
    Response:
        {
            "original": str,
            "filtered": str,
            "is_profane": bool,
            "profane_probability": float,
            "non_profane_probability": float,
            "label": str,
            "mode": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        mode = data.get('mode', 'full')
        threshold = data.get('threshold', 0.5)
        
        if not text or not text.strip():
            return jsonify({
                'error': 'Text cannot be empty'
            }), 400
        
        if mode not in ['full', 'word', 'aggressive']:
            return jsonify({
                'error': 'Invalid mode. Must be one of: full, word, aggressive'
            }), 400
        
        if threshold != profanity_filter.threshold:
            profanity_filter.threshold = threshold
        
        result = profanity_filter.filter(text, mode=mode)
        result['mode'] = mode
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/check-image', methods=['POST'])
def check_image():
    """
    Check if an uploaded image contains profane/NSFW content.
    
    Request:
        multipart/form-data with 'image' file
    
    Response:
        {
            "is_profane": bool,
            "label": str,
            "confidence": float,
            "all_scores": dict
        }
    """
    try:
        # Check if image file is in request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Check image for profanity
            result = image_checker.check_image(filepath)
            return jsonify(result), 200
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': profanity_filter is not None,
        'image_checker_loaded': image_checker is not None
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
