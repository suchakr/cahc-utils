<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
  import { SPHERE_RADIUS, COLORS, ALPHA } from '../celestial/constants.js';
  import { calculateCoordinates, generateInitialStarPosition } from '../celestial/CoordinateCalculator.js';
  import { createGrids } from './GridRenderer.js';
  import { createAxes } from './AxisRenderer.js';
  import { createMarkers } from './MarkerRenderer.js';
  import { createStar } from './StarController.js';
  import { createArcs, updateArcs } from './ArcRenderer.js';
  import { createLabelRenderer, updateLabelRendererSize } from './LabelRenderer.js';
  import { createGreatCircles, updateGreatCircles } from './GreatCircleRenderer.js';

  export let showEquatorialGrid;
  export let showEclipticGrid;
  export let showEquator;
  export let showEcliptic;
  export let showStar;
  export let showEquatorialArcs;
  export let showEclipticArcs;
  export let showPolarArcs;
  export let showLabels;
  export let showPSCircle;
  export let showPPrimeCircle;

  const dispatch = createEventDispatcher();
  
  let container;
  let scene, camera, renderer, controls, labelRenderer;
  let sphere;
  let grids = {};
  let axes = {};
  let markers = {};
  let star;
  let arcs = {};
  let greatCircles = {};
  let isDragging = false;
  let starPosition = { x: 0, y: 0, z: 0 };

  onMount(() => {
    initScene();
    animate();
    
    // Initial star position (matching screenshot)
    starPosition = generateInitialStarPosition();
    star.position.set(starPosition.x, starPosition.y, starPosition.z);
    updateCoordinates();
    
    return () => {
      renderer.dispose();
      controls.dispose();
      if (labelRenderer && labelRenderer.domElement && labelRenderer.domElement.parentNode) {
        labelRenderer.domElement.parentNode.removeChild(labelRenderer.domElement);
      }
    };
  });

  function initScene() {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);

    // Camera setup
    camera = new THREE.PerspectiveCamera(
      60,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    // Position camera to match screenshot view (from right-front, slightly elevated)
    //camera.position.set(180, 20, 150);
    camera.position.set(100, 40, -50);
    camera.lookAt(0, 0, 0);
  

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Label renderer for 3D text
    labelRenderer = createLabelRenderer(container);

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 20;
    controls.maxDistance = 35

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);

    // Celestial sphere (translucent wireframe)
    const sphereGeometry = new THREE.SphereGeometry(SPHERE_RADIUS, 64, 64);
    const sphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x444444,
      wireframe: true,
      transparent: true,
      opacity: 0.1
    });
    sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    scene.add(sphere);

    // Create grids
    grids = createGrids(scene);
    
    // Create axes
    axes = createAxes(scene);
    
    // Create markers
    markers = createMarkers(scene);
    
    // Create star
    star = createStar(scene, onStarDragStart, onStarDrag, onStarDragEnd);
    
    // Attach star event listeners
    star.userData.attachListeners(camera, renderer);
    
    // Create arcs (initially empty)
    arcs = createArcs(scene);
    
    // Create great circles (initially empty)
    greatCircles = createGreatCircles(scene);

    // Handle window resize
    window.addEventListener('resize', onWindowResize);
  }

  function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    updateLabelRendererSize(labelRenderer, container.clientWidth, container.clientHeight);
  }

  function onStarDragStart() {
    isDragging = true;
    controls.enabled = false;
  }

  function onStarDrag(position) {
    starPosition = position;
    updateCoordinates();
  }

  function onStarDragEnd() {
    isDragging = false;
    controls.enabled = true;
  }

  function updateCoordinates() {
    const coords = calculateCoordinates(starPosition.x, starPosition.y, starPosition.z);
    dispatch('coordinateUpdate', coords);
    
    // Update arcs based on new position
    updateArcs(arcs, starPosition, coords, showEquatorialArcs, showEclipticArcs, showPolarArcs, showLabels);
    
    // Update great circles based on new position
    updateGreatCircles(greatCircles, starPosition, showPSCircle, showPPrimeCircle);
  }
  
  function updateCameraAngles() {
    if (!camera) return;
    
    // Calculate azimuth (horizontal angle from +Z axis, counter-clockwise)
    const x = camera.position.x;
    const z = camera.position.z;
    let azimuth = Math.atan2(x, z) * 180 / Math.PI;
    if (azimuth < 0) azimuth += 360;
    
    // Calculate elevation (angle above horizontal plane)
    const y = camera.position.y;
    const horizontalDist = Math.sqrt(x * x + z * z);
    const elevation = Math.atan2(y, horizontalDist) * 180 / Math.PI;
    
    // Calculate distance from origin
    const distance = Math.sqrt(x * x + y * y + z * z);
    
    dispatch('cameraUpdate', {
      azimuth,
      elevation,
      distance
    });
  }

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    updateCameraAngles(); // Update camera angles every frame
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }

  // Reactively update visibility
  $: if (grids.equatorial) grids.equatorial.visible = showEquatorialGrid;
  $: if (grids.ecliptic) grids.ecliptic.visible = showEclipticGrid;
  $: if (axes.equator) axes.equator.visible = showEquator;
  $: if (axes.ecliptic) axes.ecliptic.visible = showEcliptic;
  $: if (star) star.visible = showStar;
  $: if (arcs.equatorialGroup) arcs.equatorialGroup.visible = showEquatorialArcs;
  $: if (arcs.eclipticGroup) arcs.eclipticGroup.visible = showEclipticArcs;
  $: if (arcs.polarGroup) arcs.polarGroup.visible = showPolarArcs;
  
  // Update arcs when visibility changes (to add/remove labels)
  $: if (arcs.equatorialGroup && starPosition.x !== 0) {
    updateArcs(arcs, starPosition, calculateCoordinates(starPosition.x, starPosition.y, starPosition.z), showEquatorialArcs, showEclipticArcs, showPolarArcs, showLabels);
  }
  
  // Update great circles when visibility changes
  $: if (greatCircles.psCircle && starPosition.x !== 0) {
    updateGreatCircles(greatCircles, starPosition, showPSCircle, showPPrimeCircle);
  }
</script>

<div class="canvas-container" bind:this={container}></div>

<style>
  .canvas-container {
    width: 100%;
    height: 100%;
    position: relative;
  }
</style>
