"""
Module voor het converteren van tekst naar 3D modellen
"""

def generate_3d_model(text):
    """
    Genereert een 3D model van de opgegeven tekst.
    
    Parameters:
        text (str): De tekst die naar 3D geconverteerd moet worden
        
    Returns:
        dict: Een dictionary met de 3D modelgegevens in een Three.js compatibel formaat
    """
    # Basis implementatie - deze functie zal later uitgebreid worden
    # met echte 3D model generatie
    
    # Voor nu geven we eenvoudige geometrische informatie terug
    # die door Three.js gebruikt kan worden
    model_data = {
        'text': text,
        'font': 'helvetiker',
        'size': 0.5,
        'height': 0.2,
        'curveSegments': 12,
        'bevelEnabled': True,
        'bevelThickness': 0.03,
        'bevelSize': 0.02,
        'bevelOffset': 0,
        'bevelSegments': 5
    }
    
    return model_data
