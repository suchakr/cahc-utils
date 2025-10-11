/**
 * Axis rendering for equator and ecliptic
 */

import * as THREE from 'three';
import { SPHERE_RADIUS, COLORS, ALPHA, DEG_TO_RAD, OBLIQUITY_J2000 } from '../celestial/constants.js';

/**
 * Create equator and ecliptic axes
 * @param {THREE.Scene} scene - Three.js scene
 * @returns {object} Object containing axis meshes
 */
export function createAxes(scene) {
  const equator = createEquator();
  const ecliptic = createEcliptic();
  
  scene.add(equator);
  scene.add(ecliptic);
  
  return {
    equator,
    ecliptic
  };
}

/**
 * Create equator (dashed green circle to distinguish from arcs)
 */
function createEquator() {
  const material = new THREE.LineDashedMaterial({
    color: COLORS.EQUATORIAL,
    transparent: true,
    opacity: ALPHA.AXIS,
    linewidth: 2,
    dashSize: 0.3,
    gapSize: 0.15
  });

  const segmentCount = 256; // Very smooth
  const points = [];
  
  for (let i = 0; i <= segmentCount; i++) {
    const angle = (i / segmentCount) * Math.PI * 2;
    const x = SPHERE_RADIUS * Math.cos(angle);
    const y = 0; // Equator is at y=0
    const z = -SPHERE_RADIUS * Math.sin(angle);
    points.push(new THREE.Vector3(x, y, z));
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const line = new THREE.Line(geometry, material);
  line.computeLineDistances(); // Required for dashed lines
  return line;
}

/**
 * Create ecliptic (dashed blue circle to distinguish from arcs, tilted by obliquity)
 */
function createEcliptic() {
  const material = new THREE.LineDashedMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: ALPHA.AXIS,
    linewidth: 2,
    dashSize: 0.3,
    gapSize: 0.15
  });

  const segmentCount = 256;
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  const points = [];
  
  for (let i = 0; i <= segmentCount; i++) {
    const angle = (i / segmentCount) * Math.PI * 2;
    const x = SPHERE_RADIUS * Math.cos(angle);
    const yEcl = 0; // On ecliptic plane
    const z = -SPHERE_RADIUS * Math.sin(angle);
    
    // Rotate by obliquity to align with equatorial frame
    const y = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
    const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
    
    points.push(new THREE.Vector3(x, y, zRot));
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const line = new THREE.Line(geometry, material);
  line.computeLineDistances(); // Required for dashed lines
  return line;
}
