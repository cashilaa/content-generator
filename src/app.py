from flask import Flask, render_template, request, jsonify
from content_generation.generator import ContentGenerator
from content_moderation.moderator import ContentModerator
from bias_detection.bias_detector import BiasDetector
from feedback_loop.feedback_handler import FeedbackHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

content_generator = ContentGenerator()
content_moderator = ContentModerator()
bias_detector = BiasDetector()
feedback_handler = FeedbackHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    user_interests = request.form['interests'].split(',')
    
    content = content_generator.generate_content(prompt, user_interests)
    is_appropriate, moderation_result = content_moderator.moderate_content(content)
    bias_detected, bias_result = bias_detector.detect_bias(content)
    
    if is_appropriate and not bias_detected:
        return jsonify({'status': 'success', 'content': content})
    elif not is_appropriate:
        return jsonify({'status': 'error', 'message': f"Content generation failed due to guideline violations: {moderation_result}"})
    else:
        return jsonify({'status': 'error', 'message': f"Content generation failed due to detected bias: {bias_result}"})

@app.route('/feedback', methods=['POST'])
def feedback():
    content = request.form['content']
    reaction = request.form['reaction']
    feedback_handler.add_feedback(content, reaction)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)