"""
Module voor het converteren van tekst naar 3D modellen
"""

def generate_3d_model(text, font='helvetiker', color='0x156289', bevel_color=None, thickness=0.2, position=None, bevel_enabled=True, bevel_thickness=0.03, bevel_size=0.02, bevel_segments=5, rotation_pattern='horizontal', rotation_speed='normal'):
    """
    Genereert een 3D model van de opgegeven tekst met geavanceerde opties.
    
    Parameters:
        text (str): De tekst die naar 3D geconverteerd moet worden
        font (str): Het te gebruiken lettertype ('helvetiker', 'optimer', 'gentilis', 'droid', 'opensans', 'roboto')
        color (str): De kleur van het 3D model in hexadecimale notatie (bijv. '0x156289')
        bevel_color (str, optional): De kleur van de bevel/rand in hexadecimale notatie, als None dan wordt 'color' gebruikt
        thickness (float): De dikte/hoogte van het 3D model
        position (dict, optional): Positie van het model {x: float, y: float, z: float}
        bevel_enabled (bool): Of de afgeronde randen (bevel) ingeschakeld moeten zijn
        bevel_thickness (float): De dikte van de bevel
        bevel_size (float): De grootte van de bevel
        bevel_segments (int): Het aantal segmenten in de bevel
        rotation_pattern (str): Het rotatiepatroon ('horizontal', 'vertical', 'diagonal', 'oscillating', 'breathing', 'combined')
        rotation_speed (str): De rotatiesnelheid ('slow', 'normal', 'fast', of een numerieke waarde)
        
    Returns:
        dict: Een dictionary met de 3D modelgegevens in een Three.js compatibel formaat
    """
    # Valideer en verwerk parameters
    available_fonts = ['helvetiker', 'optimer', 'gentilis', 'droid', 'opensans', 'roboto']
    
    # Valideer het lettertype en gebruik een standaardwaarde indien nodig
    if font not in available_fonts:
        font = 'helvetiker'
    
    # Valideer de kleuren (moeten hexadecimale strings zijn beginnend met '0x')
    # Standaard gebruiken we een blauw als de hoofdkleur niet geldig is
    if not color.startswith('0x') or len(color) != 8:
        color = '0x156289'
    
    # Als geen bevel kleur is opgegeven, gebruik dan dezelfde kleur als de hoofdkleur
    if not bevel_color:
        bevel_color = color
    elif not bevel_color.startswith('0x') or len(bevel_color) != 8:
        bevel_color = color
    
    # Valideer de dikte
    try:
        thickness = float(thickness)
        if thickness <= 0 or thickness > 1.5:
            thickness = 0.2
    except (ValueError, TypeError):
        thickness = 0.2
    
    # Valideer bevel parameters
    try:
        bevel_enabled = bool(bevel_enabled)
    except (ValueError, TypeError):
        bevel_enabled = True
        
    try:
        bevel_thickness = float(bevel_thickness)
        if bevel_thickness < 0 or bevel_thickness > 0.1:
            bevel_thickness = 0.03
    except (ValueError, TypeError):
        bevel_thickness = 0.03
        
    try:
        bevel_size = float(bevel_size)
        if bevel_size < 0 or bevel_size > 0.1:
            bevel_size = 0.02
    except (ValueError, TypeError):
        bevel_size = 0.02
        
    try:
        bevel_segments = int(bevel_segments)
        if bevel_segments < 1 or bevel_segments > 10:
            bevel_segments = 5
    except (ValueError, TypeError):
        bevel_segments = 5
    
    # Valideer rotatiepatroon
    available_patterns = ['horizontal', 'vertical', 'diagonal', 'oscillating', 'breathing', 'combined']
    if rotation_pattern not in available_patterns:
        rotation_pattern = 'horizontal'
    
    # Valideer rotatiesnelheid
    available_speeds = ['slow', 'normal', 'fast']
    if rotation_speed not in available_speeds:
        try:
            # Probeer te converteren naar een float als het een aangepaste snelheid is
            float_speed = float(rotation_speed)
            # Begrens de aangepaste snelheid tussen 0.1 en 5.0
            if float_speed < 0.1 or float_speed > 5.0:
                rotation_speed = 'normal'
            else:
                rotation_speed = str(float_speed)
        except (ValueError, TypeError):
            rotation_speed = 'normal'
    
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
        'bevelEnabled': bevel_enabled,
        'bevelThickness': bevel_thickness,
        'bevelSize': bevel_size,
        'bevelOffset': 0,
        'bevelSegments': bevel_segments,
        'color': color,
        'bevelColor': bevel_color,
        'position': position,
        'rotationPattern': rotation_pattern,
        'rotationSpeed': rotation_speed
    }
    
    return model_data
