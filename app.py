from flask import Flask, render_template, request, jsonify
import text_to_3d

app = Flask(__name__)

@app.route('/')
def index():
    """Rendert de hoofdpagina"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """API endpoint voor het genereren van 3D text modellen"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Geen tekst opgegeven'}), 400
    
    # Genereer 3D model data
    model_data = text_to_3d.generate_3d_model(text)
    
    return jsonify({'model_data': model_data})

def start_server(host='0.0.0.0', port=5000):
    """Start de Flask webserver"""
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    start_server()
