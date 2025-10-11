/**
 * Draggable star controller
 */

import * as THREE from 'three';
import { STAR_SIZE, COLORS, SPHERE_RADIUS } from '../celestial/constants.js';
import { createLabel } from './LabelRenderer.js';

/**
 * Create star shape geometry
 */
function createStarShape(size) {
  const shape = new THREE.Shape();
  const outerRadius = size;
  const innerRadius = size * 0.4;
  const points = 5;
  
  for (let i = 0; i < points * 2; i++) {
    const radius = i % 2 === 0 ? outerRadius : innerRadius;
    const angle = (i * Math.PI) / points - Math.PI / 2;
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    
    if (i === 0) {
      shape.moveTo(x, y);
    } else {
      shape.lineTo(x, y);
    }
  }
  
  shape.closePath();
  
  const geometry = new THREE.ShapeGeometry(shape);
  return geometry;
}

/**
 * Create draggable star
 * @param {THREE.Scene} scene - Three.js scene
 * @param {Function} onDragStart - Callback when drag starts
 * @param {Function} onDrag - Callback during drag with position
 * @param {Function} onDragEnd - Callback when drag ends
 * @returns {THREE.Mesh} Star mesh
 */
export function createStar(scene, onDragStart, onDrag, onDragEnd) {
  const geometry = createStarShape(STAR_SIZE * 1.5);
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.STAR,
    emissive: COLORS.STAR,
    emissiveIntensity: 0.5,
    side: THREE.DoubleSide
  });
  
  const star = new THREE.Mesh(geometry, material);
  
  // Make star always face camera
  star.onBeforeRender = function(renderer, scene, camera) {
    star.quaternion.copy(camera.quaternion);
  };
  
  scene.add(star);
  
  // Add label
  const label = createLabel('S', 
    { x: 0, y: 0, z: 0 },
    '#fef3c7'
  );
  star.add(label); // Attach to star so it moves with it
  label.position.set(0, 0.5, 0); // Offset above star
  
  // Raycasting for mouse interaction
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let isDragging = false;
  
  // Create invisible sphere for raycasting
  const dragSphereGeometry = new THREE.SphereGeometry(SPHERE_RADIUS, 64, 64);
  const dragSphereMaterial = new THREE.MeshBasicMaterial({
    visible: false
  });
  const dragSphere = new THREE.Mesh(dragSphereGeometry, dragSphereMaterial);
  scene.add(dragSphere);
  
  function onMouseDown(event) {
    updateMousePosition(event);
    
    // Check if clicking on star
    raycaster.setFromCamera(mouse, scene.userData.camera);
    const intersects = raycaster.intersectObject(star);
    
    if (intersects.length > 0) {
      isDragging = true;
      onDragStart();
      scene.userData.renderer.domElement.style.cursor = 'grabbing';
    }
  }
  
  function onMouseMove(event) {
    if (!isDragging) return;
    
    updateMousePosition(event);
    
    // Raycast to sphere surface
    raycaster.setFromCamera(mouse, scene.userData.camera);
    const intersects = raycaster.intersectObject(dragSphere);
    
    if (intersects.length > 0) {
      const point = intersects[0].point;
      
      // Normalize to sphere radius
      const len = Math.sqrt(point.x ** 2 + point.y ** 2 + point.z ** 2);
      const normalized = {
        x: (point.x / len) * SPHERE_RADIUS,
        y: (point.y / len) * SPHERE_RADIUS,
        z: (point.z / len) * SPHERE_RADIUS
      };
      
      star.position.set(normalized.x, normalized.y, normalized.z);
      onDrag(normalized);
    }
  }
  
  function onMouseUp() {
    if (isDragging) {
      isDragging = false;
      onDragEnd();
      scene.userData.renderer.domElement.style.cursor = 'default';
    }
  }
  
  function updateMousePosition(event) {
    const rect = scene.userData.renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }
  
  // Attach event listeners to renderer's canvas
  // Note: These will be attached after scene.userData is set in SphereCanvas
  star.userData.attachListeners = (camera, renderer) => {
    scene.userData.camera = camera;
    scene.userData.renderer = renderer;
    
    renderer.domElement.addEventListener('mousedown', onMouseDown);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('mouseup', onMouseUp);
    renderer.domElement.addEventListener('mouseleave', onMouseUp);
    
    // Hover effect
    renderer.domElement.addEventListener('mousemove', (event) => {
      if (isDragging) return;
      
      updateMousePosition(event);
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObject(star);
      
      renderer.domElement.style.cursor = intersects.length > 0 ? 'grab' : 'default';
    });
  };
  
  return star;
}
