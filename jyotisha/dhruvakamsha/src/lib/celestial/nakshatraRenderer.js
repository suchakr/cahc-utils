/**
 * Nakshatra constellation renderer
 * Renders constellation lines and labels on the celestial sphere
 */

import * as THREE from 'three';
import { SPHERE_RADIUS, COLORS, DEG_TO_RAD, OBLIQUITY_J2000 } from './constants.js';
import { getNakshatraData } from './nakshatraData.js';
import { createLabel } from '../three/LabelRenderer.js';

// Nakshatra line style
const NAKSHATRA_COLOR = COLORS.ECLIPTIC; // Blue like ecliptic
const NAKSHATRA_OPACITY = 0.7; // Higher than ecliptic (0.4)
const DASH_SIZE = 0.3;
const GAP_SIZE = 0.15;

/**
 * Convert ecliptic coordinates to Cartesian
 * @param {number} lon - Ecliptic longitude in degrees
 * @param {number} lat - Ecliptic latitude in degrees
 * @param {number} radius - Sphere radius
 * @returns {object} {x, y, z} Cartesian coordinates
 */
function eclipticToCartesian(lon, lat, radius = SPHERE_RADIUS) {
  const lonRad = lon * DEG_TO_RAD;
  const latRad = lat * DEG_TO_RAD;
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  
  // Convert to Cartesian in ecliptic frame
  const x = radius * Math.cos(latRad) * Math.cos(lonRad);
  const yEcl = radius * Math.sin(latRad);
  const z = -radius * Math.cos(latRad) * Math.sin(lonRad);
  
  // Rotate by obliquity to align with equatorial frame
  const y = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
  const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
  
  return { x, y, z: zRot };
}

/**
 * Create nakshatra constellation lines and labels
 * @param {THREE.Scene} scene - Three.js scene
 * @param {THREE.CSS2DRenderer} labelRenderer - Label renderer for CSS2D labels
 * @param {object} options - Configuration options
 * @returns {object} Nakshatra object with methods and references
 */
export function createNakshatras(scene, labelRenderer, options = {}) {
  const {
    showLines = true,
    showLabels = true
  } = options;
  
  const group = new THREE.Group();
  const linesGroup = new THREE.Group();
  const starsGroup = new THREE.Group();
  const labelsGroup = new THREE.Group();
  
  const { nakshatras, warnings } = getNakshatraData();
  
  // Log warnings if any
  if (warnings.length > 0) {
    console.warn('Nakshatra data warnings:');
    warnings.forEach(w => console.warn(w));
  }
  
  // Create line segments for each nakshatra
  const lineMaterial = new THREE.LineDashedMaterial({
    color: NAKSHATRA_COLOR,
    transparent: true,
    opacity: NAKSHATRA_OPACITY,
    dashSize: DASH_SIZE,
    gapSize: GAP_SIZE
  });
  
  // Create star dot material
  const starDotMaterial = new THREE.MeshBasicMaterial({
    color: NAKSHATRA_COLOR,
    transparent: true,
    opacity: 0.85
  });
  
  const starDotGeometry = new THREE.SphereGeometry(0.12, 16, 16);
  
  // Track unique HIP positions to avoid duplicate dots
  const uniqueStars = new Map();
  
  const nakshatraObjects = [];
  
  nakshatras.forEach(nakshatra => {
    const nakshatraGroup = new THREE.Group();
    nakshatraGroup.userData.nakshatra = nakshatra;
    
    // Create line segments
    nakshatra.segments.forEach(segment => {
      const from = eclipticToCartesian(segment.from.lon, segment.from.lat);
      const to = eclipticToCartesian(segment.to.lon, segment.to.lat);
      
      // Add star dots at each position (avoid duplicates)
      const fromKey = `${segment.from.hip}`;
      const toKey = `${segment.to.hip}`;
      
      if (!uniqueStars.has(fromKey)) {
        const starDot = new THREE.Mesh(starDotGeometry, starDotMaterial);
        starDot.position.set(from.x, from.y, from.z);
        starsGroup.add(starDot);
        uniqueStars.set(fromKey, true);
      }
      
      if (!uniqueStars.has(toKey)) {
        const starDot = new THREE.Mesh(starDotGeometry, starDotMaterial);
        starDot.position.set(to.x, to.y, to.z);
        starsGroup.add(starDot);
        uniqueStars.set(toKey, true);
      }
      
      const points = [
        new THREE.Vector3(from.x, from.y, from.z),
        new THREE.Vector3(to.x, to.y, to.z)
      ];
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, lineMaterial);
      line.computeLineDistances(); // Required for dashed lines
      
      nakshatraGroup.add(line);
    });
    
    // Create label at representative star position
    const repPos = eclipticToCartesian(
      nakshatra.repStar.lon,
      nakshatra.repStar.lat,
      SPHERE_RADIUS * 1.02 // Slightly outside sphere
    );
    
    // const labelText = nakshatra.name.firstTwoChars; // First two Devanagari characters
    const labelText = nakshatra.name.devanagari; // First two Devanagari characters
    const label = createLabel(
      labelText,
      repPos,
    //   '#60a5fa', // Blue color
      '#fa607fff', // Blue color
      'nakshatra-label'
    );
    
    // Store full name for tooltip/interaction
    label.element.title = `${nakshatra.name.devanagari} (${nakshatra.name.iast}) ${nakshatra.name.notation}`;
    
    // Remove box styling - just text with shadow
    label.element.style.fontSize = '18px';
    label.element.style.fontWeight = '700';
    label.element.style.opacity = '0.2';
    label.element.style.padding = '0';
    label.element.style.background = 'none';
    label.element.style.border = 'none';
    label.element.style.borderRadius = '0';
    label.element.style.textShadow = '0 0 3px rgba(0,0,0,0.9), 0 0 6px rgba(0,0,0,0.7)';
    
    labelsGroup.add(label);
    
    linesGroup.add(nakshatraGroup);
    nakshatraObjects.push({
      nakshatra,
      group: nakshatraGroup,
      label
    });
  });
  
  group.add(linesGroup);
  group.add(starsGroup);
  scene.add(group);
  
  // Only add labels to scene if they should be shown initially
  // CSS2DRenderer doesn't respect Three.js visible property, so we must add/remove from scene
  if (showLabels) {
    scene.add(labelsGroup);
  }
  
  // Set initial visibility for lines/stars
  linesGroup.visible = showLines;
  starsGroup.visible = showLines; // Stars follow lines visibility
  
  return {
    group,
    linesGroup,
    starsGroup,
    labelsGroup,
    nakshatras: nakshatraObjects,
    warnings,
    scene, // Store scene reference for add/remove operations
    
    // Methods to control visibility
    setVisible(visible) {
      group.visible = visible;
    },
    
    setLinesVisible(visible) {
      linesGroup.visible = visible;
      starsGroup.visible = visible; // Stars follow lines
    },
    
    setLabelsVisible(visible) {
      // CSS2DRenderer doesn't respect Three.js visible property
      // AND doesn't automatically remove DOM elements when removed from scene
      // We must both add/remove from scene AND manually hide DOM elements
      
      if (visible) {
        // Add to scene
        if (!labelsGroup.parent) {
          scene.add(labelsGroup);
        }
        // Show DOM elements
        labelsGroup.children.forEach(label => {
          if (label.element) {
            label.element.style.display = '';
          }
        });
      } else {
        // Remove from scene
        if (labelsGroup.parent) {
          scene.remove(labelsGroup);
        }
        // Hide DOM elements (they persist in DOM even after scene.remove!)
        labelsGroup.children.forEach(label => {
          if (label.element) {
            label.element.style.display = 'none';
          }
        });
      }
    },
    
    dispose() {
      // Dispose geometries and materials
      linesGroup.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      starsGroup.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      
      scene.remove(group);
      scene.remove(labelsGroup);
    }
  };
}

/**
 * Update nakshatra visibility
 * @param {object} nakshatraObject - Nakshatra object returned by createNakshatras
 * @param {boolean} visible - Visibility state
 */
export function updateNakshatraVisibility(nakshatraObject, visible) {
  if (nakshatraObject && nakshatraObject.setVisible) {
    nakshatraObject.setVisible(visible);
  }
}

/**
 * Remove nakshatras from scene
 * @param {object} nakshatraObject - Nakshatra object returned by createNakshatras
 */
export function removeNakshatras(nakshatraObject) {
  if (nakshatraObject && nakshatraObject.dispose) {
    nakshatraObject.dispose();
  }
}
