"""
Module voor het converteren van tekst naar 3D modellen
"""

def generate_3d_model(text, font='helvetiker', color='0x156289', thickness=0.2, position=None):
    """
    Genereert een 3D model van de opgegeven tekst met geavanceerde opties.
    
    Parameters:
        text (str): De tekst die naar 3D geconverteerd moet worden
        font (str): Het te gebruiken lettertype ('helvetiker', 'optimer', 'gentilis', 'droid')
        color (str): De kleur van het 3D model in hexadecimale notatie (bijv. '0x156289')
        thickness (float): De dikte/hoogte van het 3D model
        position (dict, optional): Positie van het model {x: float, y: float, z: float}
        
    Returns:
        dict: Een dictionary met de 3D modelgegevens in een Three.js compatibel formaat
    """
    # Valideer en verwerk parameters
    available_fonts = ['helvetiker', 'optimer', 'gentilis', 'droid']
    
    # Valideer het lettertype en gebruik een standaardwaarde indien nodig
    if font not in available_fonts:
        font = 'helvetiker'
    
    # Valideer de kleur (moet een hexadecimale string zijn)
    # Standaard gebruiken we een blauw als de kleur niet geldig is
    if not color.startswith('0x') or len(color) != 8:
        color = '0x156289'
    
    # Valideer de dikte
    try:
        thickness = float(thickness)
        if thickness <= 0 or thickness > 1:
            thickness = 0.2
    except (ValueError, TypeError):
        thickness = 0.2
    
    # Standaardpositie als er geen is opgegeven
    if not position or not isinstance(position, dict):
        position = {'x': 0, 'y': 0, 'z': 0}
    
    # Stel de modelgegevens samen
    model_data = {
        'text': text,
        'font': font,
        'size': 0.5,
        'height': thickness,
        'curveSegments': 12,
        'bevelEnabled': True,
        'bevelThickness': 0.03,
        'bevelSize': 0.02,
        'bevelOffset': 0,
        'bevelSegments': 5,
        'color': color,
        'position': position
    }
    
    return model_data
