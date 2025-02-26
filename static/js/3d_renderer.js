// 3D renderer using Three.js

// Globale variabelen voor Three.js componenten
let scene, camera, renderer;
let textMesh;
let fontLoader;
let fonts = {};
let currentAnimation = null; // Om de huidige animatie bij te houden
let animationParams = {
    pattern: 'horizontal',
    speed: 'normal',
    // Parameters voor specifieke animaties
    oscillating: {
        direction: 1,
        angle: 0,
        maxAngle: Math.PI / 6 // 30 graden
    },
    breathing: {
        direction: 1,
        scale: 1,
        minScale: 0.9,
        maxScale: 1.1
    }
};

// Initialiseer de 3D scene
function initScene() {
    try {
        // Controleer of THREE beschikbaar is
        if (typeof THREE === 'undefined') {
            console.error('THREE is not defined. Zorg ervoor dat Three.js correct is geladen.');
            return null;
        }
        
        // Maak een nieuwe scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0);
        
        // Bepaal de grootte van de container
        const container = document.getElementById('3d-container');
        const width = container.clientWidth || window.innerWidth * 0.8;
        const height = container.clientHeight || window.innerHeight * 0.6;
        
        // Maak een camera met perspectief
        camera = new THREE.PerspectiveCamera(
            75, // Field of view
            width / height, // Aspect ratio
            0.1, // Near clipping plane
            1000 // Far clipping plane
        );
        camera.position.z = 5;
        
        // Maak een renderer en voeg deze toe aan de DOM
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        
        // Verwijder bestaande children van de container
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
        container.appendChild(renderer.domElement);
        
        // Voeg belichting toe
        const ambientLight = new THREE.AmbientLight(0x888888);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(0, 1, 1);
        scene.add(directionalLight);
        
        // Tweede licht van onderaf voor betere belichting van de bevel
        const bottomLight = new THREE.DirectionalLight(0xffffff, 0.3);
        bottomLight.position.set(0, -1, 0);
        scene.add(bottomLight);
        
        // Controleer of FontLoader beschikbaar is
        if (typeof THREE.FontLoader === 'undefined') {
            console.error('THREE.FontLoader is not defined. Zorg ervoor dat FontLoader correct is geladen.');
            return null;
        }
        
        // Initialiseer de font loader
        fontLoader = new THREE.FontLoader();
        
        // Maak de scene responsive
        window.addEventListener('resize', () => {
            const newWidth = container.clientWidth || window.innerWidth * 0.8;
            const newHeight = container.clientHeight || window.innerHeight * 0.6;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
        });
        
        // Render de scene eenmalig om te laten zien dat het werkt
        renderer.render(scene, camera);
        
        console.log('Three.js scene succesvol geïnitialiseerd');
        return scene;
    } catch (error) {
        console.error('Fout bij initialiseren van de scene:', error);
        return null;
    }
}

// Laad een lettertype en cache het
function loadFont(fontName) {
    return new Promise((resolve, reject) => {
        try {
            // Als het lettertype al in cache zit, gebruik het dan
            if (fonts[fontName]) {
                resolve(fonts[fontName]);
                return;
            }
            
            // Anders laden we het lettertype via de CDN
            // Mapping van lettertypewaarden naar URL's
            const fontUrls = {
                'helvetiker': 'https://threejs.org/examples/fonts/helvetiker_regular.typeface.json',
                'optimer': 'https://threejs.org/examples/fonts/optimer_regular.typeface.json',
                'gentilis': 'https://threejs.org/examples/fonts/gentilis_regular.typeface.json',
                'droid': 'https://threejs.org/examples/fonts/droid/droid_sans_regular.typeface.json',
                'opensans': 'https://threejs.org/examples/fonts/droid/droid_sans_regular.typeface.json', // Placeholder URL, zou moeten worden vervangen
                'roboto': 'https://threejs.org/examples/fonts/gentilis_regular.typeface.json' // Placeholder URL, zou moeten worden vervangen
            };
            
            // Controleer of we een URL hebben voor het gevraagde lettertype
            const fontUrl = fontUrls[fontName] || fontUrls['helvetiker'];
            
            console.log('Font aan het laden:', fontUrl);
            
            fontLoader.load(fontUrl, function(font) {
                // Cache het lettertype voor later gebruik
                fonts[fontName] = font;
                console.log('Font succesvol geladen:', fontName);
                resolve(font);
            }, undefined, function(error) {
                console.error('Font loading error:', error);
                reject(error);
            });
        } catch (error) {
            console.error('Fout bij laden van font:', error);
            reject(error);
        }
    });
}

// Render de 3D text met de gegeven data
function renderText(textData) {
    console.log('renderText aangeroepen met:', textData);
    
    try {
        // Initialiseer de scene als die nog niet bestaat
        if (!scene) {
            console.log('Scene initialiseren...');
            initScene();
        }
        
        // Controleer of we de nodige drie.js componenten hebben
        if (!scene || !camera || !renderer || !fontLoader) {
            console.error('Benodigde Three.js componenten zijn niet geïnitialiseerd');
            return;
        }
        
        // Verwijder bestaande textMesh als die er is
        if (textMesh) {
            console.log('Bestaande textMesh verwijderen');
            scene.remove(textMesh);
        }
        
        // Update de achtergrondkleur van de renderer container om contrast te verbeteren
        const container = document.getElementById('3d-container');
        container.style.backgroundColor = '#f0f0f0';
        
        // Controleer of THREE.TextGeometry beschikbaar is
        if (typeof THREE.TextGeometry === 'undefined') {
            console.error('THREE.TextGeometry is not defined. Zorg ervoor dat TextGeometry correct is geladen.');
            return;
        }
        
        // Laad het gewenste lettertype
        console.log('Font laden voor:', textData.font);
        
        loadFont(textData.font)
            .then(font => {
                console.log('Font geladen, textgeometry maken');
                
                // Maak geometry voor 3D tekst
                const textGeometry = new THREE.TextGeometry(textData.text, {
                    font: font,
                    size: textData.size,
                    height: textData.height,
                    curveSegments: textData.curveSegments,
                    bevelEnabled: textData.bevelEnabled,
                    bevelThickness: textData.bevelThickness,
                    bevelSize: textData.bevelSize,
                    bevelOffset: textData.bevelOffset,
                    bevelSegments: textData.bevelSegments
                });
                
                // Centreer de tekst
                textGeometry.computeBoundingBox();
                const centerOffset = -0.5 * (textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x);
                
                // Bereid materialen voor
                let materials = [];
                
                // Hoofdmateriaal voor de tekst
                const mainMaterial = new THREE.MeshPhongMaterial({
                    color: parseInt(textData.color, 16),
                    specular: 0x111111,
                    shininess: 30
                });
                
                // Als er een aparte bevelkleur is, maak dan een apart materiaal voor de bevel
                if (textData.bevelColor && textData.bevelColor !== textData.color && textData.bevelEnabled) {
                    const bevelMaterial = new THREE.MeshPhongMaterial({
                        color: parseInt(textData.bevelColor, 16),
                        specular: 0x111111,
                        shininess: 30
                    });
                    
                    // Voeg aparte materialen toe voor de verschillende delen van de mesh
                    // Index 0 is voor de voorkant, index 1 voor de zijkant (bevel)
                    materials = [
                        mainMaterial, // voorkant
                        bevelMaterial // zijkant (bevel)
                    ];
                    
                    // Markeer de geometry om verschillende materialen te kunnen gebruiken
                    // Handel het geval af voor geometrie zonder index eigenschap
                    if (textGeometry.index) {
                        textGeometry.groups = [
                            { start: 0, count: textGeometry.index.count / 2, materialIndex: 0 }, // Voorkant
                            { start: textGeometry.index.count / 2, count: textGeometry.index.count / 2, materialIndex: 1 } // Zijkant
                        ];
                    } else {
                        // Alternatieve aanpak als er geen index is
                        const totalCount = textGeometry.attributes.position.count;
                        textGeometry.groups = [
                            { start: 0, count: totalCount / 2, materialIndex: 0 }, // Voorkant
                            { start: totalCount / 2, count: totalCount / 2, materialIndex: 1 } // Zijkant
                        ];
                    }
                    
                    // Maak de mesh met geometry en materialen
                    textMesh = new THREE.Mesh(textGeometry, materials);
                } else {
                    // Eén materiaal voor alles als er geen aparte bevelkleur is
                    textMesh = new THREE.Mesh(textGeometry, mainMaterial);
                }
                
                // Positioneer de mesh
                textMesh.position.x = centerOffset;
                
                // Gebruik positie uit textData als die is opgegeven, anders standaardwaarden
                if (textData.position) {
                    if (textData.position.y !== undefined) textMesh.position.y = textData.position.y;
                    if (textData.position.z !== undefined) textMesh.position.z = textData.position.z;
                }
                
                // Voeg de mesh toe aan de scene
                console.log('TextMesh toevoegen aan scene');
                scene.add(textMesh);
                
                // Stel de nieuwe animatieparameters in
                animationParams.pattern = textData.rotationPattern || 'horizontal';
                animationParams.speed = textData.rotationSpeed || 'normal';
                
                // Reset specifieke animatieparameters
                animationParams.oscillating = {
                    direction: 1,
                    angle: 0,
                    maxAngle: Math.PI / 6
                };
                
                animationParams.breathing = {
                    direction: 1,
                    scale: 1,
                    minScale: 0.9,
                    maxScale: 1.1
                };
                
                // Start de animatie
                console.log('Animatie starten met patroon:', animationParams.pattern, 'en snelheid:', animationParams.speed);
                animateRotation();
            })
            .catch(error => {
                console.error('Error rendering text:', error);
            });
    } catch (error) {
        console.error('Onverwachte fout bij renderText:', error);
    }
}

// Bereken de rotatiesnelheid op basis van de ingestelde snelheid
function getRotationSpeed() {
    const speedMapping = {
        'slow': 0.005,
        'normal': 0.01,
        'fast': 0.02
    };
    
    // Controleer of het een voorgedefinieerde snelheid is
    if (animationParams.speed in speedMapping) {
        return speedMapping[animationParams.speed];
    }
    
    // Anders probeer het te converteren naar een getal (aangepaste snelheid)
    try {
        const customSpeed = parseFloat(animationParams.speed);
        return 0.01 * customSpeed; // De standaardsnelheid vermenigvuldigen met de aangepaste factor
    } catch (e) {
        return 0.01; // Standaard bij fout
    }
}

// Horizontale rotatie (draaien om Y-as)
function animateHorizontalRotation() {
    if (textMesh) {
        textMesh.rotation.y += getRotationSpeed();
    }
}

// Verticale rotatie (draaien om X-as)
function animateVerticalRotation() {
    if (textMesh) {
        textMesh.rotation.x += getRotationSpeed();
    }
}

// Diagonale rotatie (draaien om X-as én Y-as)
function animateDiagonalRotation() {
    if (textMesh) {
        textMesh.rotation.x += getRotationSpeed() * 0.7;
        textMesh.rotation.y += getRotationSpeed();
    }
}

// Oscillerende rotatie (heen en weer)
function animateOscillatingRotation() {
    if (textMesh) {
        const params = animationParams.oscillating;
        const speed = getRotationSpeed() * 2; // Sneller voor betere zichtbaarheid
        
        // Update de hoek
        params.angle += speed * params.direction;
        
        // Keer de richting om als de maximale hoek is bereikt
        if (Math.abs(params.angle) >= params.maxAngle) {
            params.direction *= -1;
        }
        
        // Pas de rotatie toe
        textMesh.rotation.y = params.angle;
    }
}

// Ademende animatie (schalen)
function animateBreathingEffect() {
    if (textMesh) {
        const params = animationParams.breathing;
        const speed = getRotationSpeed() * 0.5; // Langzamer voor een rustiger effect
        
        // Update de schaal
        params.scale += speed * params.direction;
        
        // Keer de richting om als de minimum of maximum schaal is bereikt
        if (params.scale <= params.minScale || params.scale >= params.maxScale) {
            params.direction *= -1;
        }
        
        // Pas de schaal toe
        textMesh.scale.set(params.scale, params.scale, params.scale);
        
        // Voeg langzame rotatie toe voor extra effect
        textMesh.rotation.y += getRotationSpeed() * 0.2;
    }
}

// Gecombineerde animatie (meerdere bewegingen)
function animateCombinedEffects() {
    if (textMesh) {
        // Rotatie
        textMesh.rotation.x += getRotationSpeed() * 0.3;
        textMesh.rotation.y += getRotationSpeed() * 0.5;
        textMesh.rotation.z += getRotationSpeed() * 0.1;
        
        // Lichte ademende beweging
        const params = animationParams.breathing;
        const speed = getRotationSpeed() * 0.2;
        
        params.scale += speed * params.direction;
        if (params.scale <= params.minScale || params.scale >= params.maxScale) {
            params.direction *= -1;
        }
        
        // Minder extreme schaal voor gecombineerde beweging
        const combinedScale = 1 + (params.scale - 1) * 0.5;
        textMesh.scale.set(combinedScale, combinedScale, combinedScale);
    }
}

// Animeer de rotatie van het 3D model op basis van het geselecteerde patroon
function animateRotation() {
    // Controleer of we de nodige drie.js componenten hebben
    if (!scene || !camera || !renderer) {
        console.error('Benodigde Three.js componenten zijn niet geïnitialiseerd voor animatie');
        return;
    }
    
    // Stop de vorige animatie als die er is
    if (currentAnimation) {
        cancelAnimationFrame(currentAnimation);
        currentAnimation = null;
    }
    
    // Animatieloop
    function animate() {
        currentAnimation = requestAnimationFrame(animate);
        
        // Kies de juiste animatiefunctie op basis van het patroon
        switch (animationParams.pattern) {
            case 'vertical':
                animateVerticalRotation();
                break;
            case 'diagonal':
                animateDiagonalRotation();
                break;
            case 'oscillating':
                animateOscillatingRotation();
                break;
            case 'breathing':
                animateBreathingEffect();
                break;
            case 'combined':
                animateCombinedEffects();
                break;
            case 'horizontal':
            default:
                animateHorizontalRotation();
                break;
        }
        
        // Render de scene met camera
        renderer.render(scene, camera);
    }
    
    // Start de animatie
    animate();
}

// Voorgedefinieerde kleurschema's
const colorSchemes = {
    'blue': { main: '#156289', bevel: '#0E4B6E' },
    'red': { main: '#AA2222', bevel: '#881111' }, 
    'green': { main: '#22AA22', bevel: '#118811' },
    'gold': { main: '#D4AF37', bevel: '#B8860B' },
    'purple': { main: '#9370DB', bevel: '#7851A9' },
    'orange': { main: '#F96D00', bevel: '#D65C00' }
};

// Helper functie om een voorgedefinieerd kleurenschema toe te passen
function applyColorScheme(schemeName) {
    if (colorSchemes[schemeName]) {
        document.getElementById('color-picker').value = colorSchemes[schemeName].main;
        document.getElementById('bevel-color-picker').value = colorSchemes[schemeName].bevel;
    }
}
