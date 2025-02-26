// 3D renderer using Three.js

// Globale variabelen voor Three.js componenten
let scene, camera, renderer;
let textMesh;
let fontLoader;
let fonts = {};

// Initialiseer de 3D scene
function initScene() {
    // Maak een nieuwe scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    // Maak een camera met perspectief
    camera = new THREE.PerspectiveCamera(
        75, // Field of view
        window.innerWidth / window.innerHeight, // Aspect ratio
        0.1, // Near clipping plane
        1000 // Far clipping plane
    );
    camera.position.z = 5;
    
    // Maak een renderer en voeg deze toe aan de DOM
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
    
    // Haal de container op en voeg de renderer toe
    const container = document.getElementById('3d-container');
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
    
    // Initialiseer de font loader
    fontLoader = new THREE.FontLoader();
    
    // Maak de scene responsive
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
    });
    
    // Render de scene
    renderer.render(scene, camera);
    
    return scene;
}

// Laad een lettertype en cache het
function loadFont(fontName) {
    return new Promise((resolve, reject) => {
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
            'droid': 'https://threejs.org/examples/fonts/droid/droid_sans_regular.typeface.json'
        };
        
        // Controleer of we een URL hebben voor het gevraagde lettertype
        const fontUrl = fontUrls[fontName] || fontUrls['helvetiker'];
        
        fontLoader.load(fontUrl, function(font) {
            // Cache het lettertype voor later gebruik
            fonts[fontName] = font;
            resolve(font);
        }, undefined, function(error) {
            console.error('Font loading error:', error);
            reject(error);
        });
    });
}

// Render de 3D text met de gegeven data
function renderText(textData) {
    // Initialiseer de scene als die nog niet bestaat
    if (!scene) {
        initScene();
    }
    
    // Verwijder bestaande textMesh als die er is
    if (textMesh) {
        scene.remove(textMesh);
    }
    
    // Laad het gewenste lettertype
    loadFont(textData.font)
        .then(font => {
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
            
            // Maak een materiaal voor de tekst met de gekozen kleur
            const textMaterial = new THREE.MeshPhongMaterial({
                color: parseInt(textData.color, 16),
                specular: 0x111111,
                shininess: 30
            });
            
            // Maak de mesh met geometry en materiaal
            textMesh = new THREE.Mesh(textGeometry, textMaterial);
            textMesh.position.x = centerOffset;
            
            // Gebruik positie uit textData als die is opgegeven, anders standaardwaarden
            if (textData.position) {
                if (textData.position.y !== undefined) textMesh.position.y = textData.position.y;
                if (textData.position.z !== undefined) textMesh.position.z = textData.position.z;
            }
            
            // Voeg de mesh toe aan de scene
            scene.add(textMesh);
            
            // Start de animatie
            animateRotation();
        })
        .catch(error => {
            console.error('Error rendering text:', error);
        });
}

// Animeer de rotatie van het 3D model
function animateRotation() {
    // Animatieloop
    function animate() {
        requestAnimationFrame(animate);
        
        // Roteer de tekst langzaam
        if (textMesh) {
            textMesh.rotation.y += 0.01;
        }
        
        // Render de scene met camera
        renderer.render(scene, camera);
    }
    
    // Start de animatie
    animate();
}
