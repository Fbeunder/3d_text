from flask import Flask, render_template, request, jsonify
import text_to_3d

app = Flask(__name__)

@app.route('/')
def index():
    """Rendert de hoofdpagina"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """API endpoint voor het genereren van 3D text modellen met geavanceerde opties"""
    data = request.get_json()
    
    # Haal alle parameters uit het request
    text = data.get('text', '')
    font = data.get('font', 'helvetiker')
    color = data.get('color', '0x156289')
    bevel_color = data.get('bevelColor')  # Kan None zijn
    thickness = data.get('thickness', 0.2)
    position = data.get('position', None)
    
    # Haal bevel parameters uit het request
    bevel_enabled = data.get('bevelEnabled', True)
    bevel_thickness = data.get('bevelThickness', 0.03)
    bevel_size = data.get('bevelSize', 0.02)
    bevel_segments = data.get('bevelSegments', 5)
    
    if not text:
        return jsonify({'error': 'Geen tekst opgegeven'}), 400
    
    # Genereer 3D model data met alle parameters
    model_data = text_to_3d.generate_3d_model(
        text=text,
        font=font,
        color=color,
        bevel_color=bevel_color,
        thickness=thickness,
        position=position,
        bevel_enabled=bevel_enabled,
        bevel_thickness=bevel_thickness,
        bevel_size=bevel_size,
        bevel_segments=bevel_segments
    )
    
    return jsonify({'model_data': model_data})

def start_server(host='0.0.0.0', port=5000):
    """Start de Flask webserver"""
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    start_server()
