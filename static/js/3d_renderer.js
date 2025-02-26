// 3D renderer using Three.js

// Globale variabelen voor Three.js componenten
let scene, camera, renderer;
let textMesh;

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
    
    // Render de scene
    renderer.render(scene, camera);
    
    // Maak de scene responsive
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
    });
    
    return scene;
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
    
    // Laad de font en maak de 3D tekst
    const loader = new THREE.FontLoader();
    loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', function(font) {
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
        
        // Maak een materiaal voor de tekst
        const textMaterial = new THREE.MeshPhongMaterial({
            color: 0x156289,
            specular: 0x156289,
            shininess: 30
        });
        
        // Maak de mesh met geometry en materiaal
        textMesh = new THREE.Mesh(textGeometry, textMaterial);
        textMesh.position.x = centerOffset;
        textMesh.position.y = 0;
        textMesh.position.z = 0;
        
        // Voeg de mesh toe aan de scene
        scene.add(textMesh);
        
        // Start de animatie
        animateRotation();
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
