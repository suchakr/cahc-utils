/**
 * Ecliptic band visualization (±23.5° from ecliptic)
 * Represents the zodiacal belt and the range of the Sun's apparent motion
 */

import * as THREE from 'three';
import { SPHERE_RADIUS, COLORS, DEG_TO_RAD, OBLIQUITY_J2000 } from './constants.js';

// Ecliptic band latitude range (±23.5° from ecliptic plane)
const BAND_LATITUDE = 23.5; // degrees

/**
 * Create the ecliptic band visualization
 * @param {THREE.Scene} scene - Three.js scene
 * @param {object} options - Configuration options
 * @param {number} options.opacity - Band opacity (default: 0.15)
 * @param {number} options.boundaryOpacity - Boundary circle opacity (default: 0.6)
 * @param {boolean} options.showBand - Show filled band (default: true)
 * @param {boolean} options.showBoundaries - Show boundary circles (default: true)
 * @returns {object} Band object with methods and references
 */
export function createEclipticBand(scene, options = {}) {
  const {
    opacity = 0.15,
    boundaryOpacity = 0.6,
    showBand = true,
    showBoundaries = true
  } = options;

  const group = new THREE.Group();
  const band = createBand(opacity);
  const northBoundary = createBoundaryCircle(BAND_LATITUDE, boundaryOpacity);
  const southBoundary = createBoundaryCircle(-BAND_LATITUDE, boundaryOpacity);

  if (showBand) {
    group.add(band);
  }
  if (showBoundaries) {
    group.add(northBoundary);
    group.add(southBoundary);
  }

  scene.add(group);

  return {
    group,
    band,
    northBoundary,
    southBoundary,
    
    // Methods to control visibility
    setVisible(visible) {
      group.visible = visible;
    },
    
    setBandVisible(visible) {
      band.visible = visible;
    },
    
    setBoundariesVisible(visible) {
      northBoundary.visible = visible;
      southBoundary.visible = visible;
    },
    
    setOpacity(newOpacity) {
      if (band.material.opacity !== undefined) {
        band.material.opacity = newOpacity;
      }
    },
    
    setBoundaryOpacity(newOpacity) {
      if (northBoundary.material.opacity !== undefined) {
        northBoundary.material.opacity = newOpacity;
      }
      if (southBoundary.material.opacity !== undefined) {
        southBoundary.material.opacity = newOpacity;
      }
    },
    
    dispose() {
      scene.remove(group);
      band.geometry.dispose();
      band.material.dispose();
      northBoundary.geometry.dispose();
      northBoundary.material.dispose();
      southBoundary.geometry.dispose();
      southBoundary.material.dispose();
    }
  };
}

/**
 * Create the filled band between ±23.5° ecliptic latitude
 * @param {number} opacity - Band opacity
 * @returns {THREE.Mesh} Band mesh
 */
function createBand(opacity) {
  const segments = 128;
  const latSegments = 32;
  
  const geometry = new THREE.BufferGeometry();
  const vertices = [];
  const indices = [];
  
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  
  // Create vertices for the band
  for (let i = 0; i <= latSegments; i++) {
    // Latitude ranges from -BAND_LATITUDE to +BAND_LATITUDE
    const lat = -BAND_LATITUDE + (i / latSegments) * (2 * BAND_LATITUDE);
    const latRad = lat * DEG_TO_RAD;
    const radius = SPHERE_RADIUS * Math.cos(latRad);
    const yEcl = SPHERE_RADIUS * Math.sin(latRad);
    
    for (let j = 0; j <= segments; j++) {
      const lon = (j / segments) * 360;
      const lonRad = lon * DEG_TO_RAD;
      
      const x = radius * Math.cos(lonRad);
      const z = -radius * Math.sin(lonRad);
      
      // Rotate by obliquity to align with equatorial frame
      const yRot = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
      const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
      
      vertices.push(x, yRot, zRot);
    }
  }
  
  // Create triangular faces
  for (let i = 0; i < latSegments; i++) {
    for (let j = 0; j < segments; j++) {
      const a = i * (segments + 1) + j;
      const b = a + segments + 1;
      const c = a + 1;
      const d = b + 1;
      
      // Two triangles per quad
      indices.push(a, b, c);
      indices.push(c, b, d);
    }
  }
  
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  
  const material = new THREE.MeshBasicMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: opacity,
    side: THREE.DoubleSide,
    depthWrite: false // Allow proper transparency
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  return mesh;
}

/**
 * Create a boundary circle at a specific ecliptic latitude
 * @param {number} latitude - Ecliptic latitude in degrees
 * @param {number} opacity - Circle opacity
 * @returns {THREE.Line} Boundary circle
 */
function createBoundaryCircle(latitude, opacity) {
  const segments = 128;
  const points = [];
  
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  const latRad = latitude * DEG_TO_RAD;
  const radius = SPHERE_RADIUS * Math.cos(latRad);
  const yEcl = SPHERE_RADIUS * Math.sin(latRad);
  
  for (let i = 0; i <= segments; i++) {
    const lon = (i / segments) * 360;
    const lonRad = lon * DEG_TO_RAD;
    
    const x = radius * Math.cos(lonRad);
    const z = -radius * Math.sin(lonRad);
    
    // Rotate by obliquity to align with equatorial frame
    const yRot = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
    const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
    
    points.push(new THREE.Vector3(x, yRot, zRot));
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: opacity
  });
  
  return new THREE.Line(geometry, material);
}

/**
 * Update ecliptic band visibility
 * @param {object} bandObject - Band object returned by createEclipticBand
 * @param {boolean} visible - Visibility state
 */
export function updateEclipticBandVisibility(bandObject, visible) {
  if (bandObject && bandObject.setVisible) {
    bandObject.setVisible(visible);
  }
}

/**
 * Remove ecliptic band from scene
 * @param {object} bandObject - Band object returned by createEclipticBand
 */
export function removeEclipticBand(bandObject) {
  if (bandObject && bandObject.dispose) {
    bandObject.dispose();
  }
}
