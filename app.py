"""
Flask Backend for Profanity Filter
Provides REST API endpoints for the profanity detection and filtering service.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from profanity_filter import ProfanityFilter
import os

app = Flask(__name__)
CORS(app)

# Initialize the profanity filter (loaded once at startup)
print("Initializing profanity filter...")
profanity_filter = ProfanityFilter(model_path="Anvesh18/zeroshot-profanity-filter", threshold=0.5)
print("Profanity filter ready!")


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
        
        # Update threshold if different from current
        if threshold != profanity_filter.threshold:
            profanity_filter.threshold = threshold
        
        result = profanity_filter.filter(text, mode=mode)
        result['mode'] = mode
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': profanity_filter is not None
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
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
