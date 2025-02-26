# 3D Text Visualizer

Een interactieve webapplicatie waarmee gebruikers tekst kunnen omzetten naar 3D-modellen en deze in realtime kunnen bekijken, aanpassen en roteren in de browser.

## Projectoverzicht

Deze applicatie maakt het mogelijk om een opgegeven naam of tekst als een 3D-model weer te geven en dit langzaam te laten ronddraaien in een webinterface. Het doel is een interactieve en visueel aantrekkelijke manier te bieden om text-to-3D visualisatie te tonen.

## Functionaliteiten

- Genereren van 3D-tekst op basis van gebruikersinvoer
- Ondersteuning voor 6 verschillende lettertypen
  - Helvetiker
  - Optimer
  - Gentilis
  - Droid Sans
  - Open Sans
  - Roboto
- Uitgebreide kleurconfiguratie
  - Keuze uit voorgedefinieerde kleurenschema's
  - Individuele kleurinstellingen voor tekst en randen
- Geavanceerde vormgevingsopties
  - Instelbare dikte van de tekst
  - Aanpasbare afgeronde randen (bevel)
  - Gedetailleerde instelmogelijkheden voor bevels
- Volledig responsieve en gebruiksvriendelijke interface

## Vereisten

### Systeemvereisten
- Python 3.8 of hoger
- Moderne webbrowser met WebGL-ondersteuning (Chrome, Firefox, Safari, Edge)

### Python Afhankelijkheden
- Flask 2.0.1
- Werkzeug 2.0.1
- Jinja2 3.0.1
- MarkupSafe 2.0.1
- itsdangerous 2.0.1
- click 8.0.1

## Installatie

1. Clone deze repository:
   ```
   git clone https://github.com/Fbeunder/3d_text.git
   cd 3d_text
   ```

2. Maak een virtuele omgeving aan (optioneel maar aanbevolen):
   ```
   python -m venv venv
   source venv/bin/activate  # Op Windows: venv\Scripts\activate
   ```

3. Installeer de vereiste pakketten:
   ```
   pip install -r requirements.txt
   ```

## Gebruik

1. Start de applicatie:
   ```
   python app.py
   ```

2. Open je webbrowser en ga naar:
   ```
   http://localhost:5000
   ```

3. Voer tekst in, pas de opties naar wens aan en klik op "Genereer 3D Text"

## Projectstructuur

```
3d_text/
├── app.py                 # Hoofdapplicatie met Flask-routes
├── text_to_3d.py          # Module voor tekstconversie naar 3D-modellen
├── requirements.txt       # Python vereisten
├── static/
│   ├── css/
│   │   └── style.css      # Styling voor de webinterface
│   └── js/
│       └── 3d_renderer.js # Client-side JavaScript voor 3D-rendering
└── templates/
    └── index.html         # Hoofdpagina HTML-template
```

## Technische Details

### Backend
- Python/Flask voor de webserver
- RESTful API-endpoint voor model generatie
- Parametrisatie van 3D-tekstmodellen

### Frontend
- HTML/CSS/JavaScript voor de gebruikersinterface
- Three.js voor 3D-rendering
- Realtime 3D-visualisatie en animatie

## Ontwikkeling

Om aan dit project bij te dragen:

1. Fork dit repository
2. Maak je wijzigingen
3. Dien een pull request in

## Licentie

[MIT License](LICENSE)

## Auteurs

- Fbeunder
