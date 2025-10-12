/**
 * Marker rendering for key celestial points
 */

import * as THREE from 'three';
import { SPHERE_RADIUS, MARKER_SIZE, COLORS, ALPHA, DEG_TO_RAD, OBLIQUITY_J2000, ASHVINI_ECLIPTIC_LON, ECLIPTIC_POLE } from '../celestial/constants.js';
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
 * Create diamond shape geometry
 */
function createDiamondShape(size) {
  const shape = new THREE.Shape();
  shape.moveTo(0, size);
  shape.lineTo(size, 0);
  shape.lineTo(0, -size);
  shape.lineTo(-size, 0);
  shape.closePath();
  
  const geometry = new THREE.ShapeGeometry(shape);
  return geometry;
}

/**
 * Create markers for key celestial points
 * @param {THREE.Scene} scene - Three.js scene
 * @returns {object} Object containing marker meshes and labels
 */
export function createMarkers(scene) {
  const eq = createVernalEquinox(scene);
  const pole = createCelestialPole(scene);
  const eclipticPole = createEclipticPole(scene);
  const ashvini = createAshvini(scene);
  
  return {
    eq: eq.marker,
    pole: pole.marker,
    eclipticPole: eclipticPole.marker,
    ashvini: ashvini.marker,
    labels: {
      eq: eq.label,
      pole: pole.label,
      eclipticPole: eclipticPole.label,
      ashvini: ashvini.label
    }
  };
}

/**
 * Create vernal equinox marker (L)
 * At RA=0°, Dec=0° (intersection of equator and ecliptic)
 */
function createVernalEquinox(scene) {
  const geometry = createDiamondShape(MARKER_SIZE * 1.2);
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.EQUATORIAL,
    transparent: true,
    opacity: ALPHA.MARKER,
    side: THREE.DoubleSide
  });
  
  const marker = new THREE.Mesh(geometry, material);
  marker.position.set(SPHERE_RADIUS * 1.05, 0, 0); // Slightly outside sphere
  
  // Make marker always face camera
  marker.onBeforeRender = function(renderer, scene, camera) {
    marker.quaternion.copy(camera.quaternion);
  };
  
  scene.add(marker);
  
  // Add label
  const label = createLabel('L', 
    { x: SPHERE_RADIUS * 1.15, y: 0, z: 0 },
    '#4ade80'
  );
  scene.add(label);
  
  return { marker, label };
}

/**
 * Create celestial pole marker (P)
 * At Dec=90° (north celestial pole)
 */
function createCelestialPole(scene) {
  const geometry = createStarShape(MARKER_SIZE * 2.0);
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.EQUATORIAL,
    transparent: true,
    opacity: ALPHA.MARKER,
    side: THREE.DoubleSide
  });
  
  const marker = new THREE.Mesh(geometry, material);
  marker.position.set(0, SPHERE_RADIUS * 1.05, 0); // North pole
  
  // Make marker always face camera
  marker.onBeforeRender = function(renderer, scene, camera) {
    marker.quaternion.copy(camera.quaternion);
  };
  
  scene.add(marker);
  
  // Add label
  const label = createLabel('P', 
    { x: 0, y: SPHERE_RADIUS * 1.15, z: 0 },
    '#4ade80'
  );
  scene.add(label);
  
  return { marker, label };
}

/**
 * Create ecliptic pole marker (P′)
 * At ecliptic latitude=90°
 */
function createEclipticPole(scene) {
  const geometry = new THREE.CircleGeometry(MARKER_SIZE * 1.3, 32);
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: ALPHA.MARKER,
    side: THREE.DoubleSide
  });
  
  const marker = new THREE.Mesh(geometry, material);
  
  // Ecliptic pole is at ecliptic latitude 90°
  // In equatorial coordinates: RA = 18h (270°), Dec = 90° - obliquity
  const raRad = ECLIPTIC_POLE.ra * DEG_TO_RAD;
  const decRad = ECLIPTIC_POLE.dec * DEG_TO_RAD;
  
  const x = SPHERE_RADIUS * 1.05 * Math.cos(decRad) * Math.cos(raRad);
  const y = SPHERE_RADIUS * 1.05 * Math.sin(decRad);
  const z = -SPHERE_RADIUS * 1.05 * Math.cos(decRad) * Math.sin(raRad);
  
  marker.position.set(x, y, z);
  
  // Make marker always face camera
  marker.onBeforeRender = function(renderer, scene, camera) {
    marker.quaternion.copy(camera.quaternion);
  };
  
  scene.add(marker);
  
  // Add label
  const label = createLabel('P′', 
    { x: x, y: y * 1.1, z: z * 1.1 },
    '#60a5fa'
  );
  scene.add(label);
  
  return { marker, label };
}

/**
 * Create Ashvini marker (L′)
 * At ecliptic longitude=34°, latitude=0°
 */
function createAshvini(scene) {
  const geometry = createDiamondShape(MARKER_SIZE * 1.3);
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.POLAR,
    transparent: true,
    opacity: ALPHA.MARKER,
    side: THREE.DoubleSide
  });
  
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  const lonRad = ASHVINI_ECLIPTIC_LON * DEG_TO_RAD;
  
  // Position on ecliptic at 34° longitude
  const x = SPHERE_RADIUS * 1.05 * Math.cos(lonRad);
  const yEcl = 0; // On ecliptic plane
  const z = -SPHERE_RADIUS * 1.05 * Math.sin(lonRad);
  
  // Rotate by obliquity to align with equatorial frame
  const y = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
  const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
  
  const marker = new THREE.Mesh(geometry, material);
  marker.position.set(x, y, zRot);
  
  // Make marker always face camera
  marker.onBeforeRender = function(renderer, scene, camera) {
    marker.quaternion.copy(camera.quaternion);
  };
  
  scene.add(marker);
  
  // Add label
  const label = createLabel('L′', 
    { x: x * 1.1, y: y * 1.1, z: zRot * 1.1 },
    '#fbbf24'
  );
  scene.add(label);
  
  return { marker, label };
}
