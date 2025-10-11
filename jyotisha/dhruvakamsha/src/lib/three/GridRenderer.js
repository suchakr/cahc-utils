/**
 * Grid rendering for equatorial and ecliptic coordinate systems
 */

import * as THREE from 'three';
import { SPHERE_RADIUS, COLORS, ALPHA, GRID_DIVISIONS, DEG_TO_RAD, OBLIQUITY_J2000 } from '../celestial/constants.js';

/**
 * Create equatorial and ecliptic grids
 * @param {THREE.Scene} scene - Three.js scene
 * @returns {object} Object containing grid meshes
 */
export function createGrids(scene) {
  const equatorialGrid = createEquatorialGrid();
  const eclipticGrid = createEclipticGrid();
  
  scene.add(equatorialGrid);
  scene.add(eclipticGrid);
  
  return {
    equatorial: equatorialGrid,
    ecliptic: eclipticGrid
  };
}

/**
 * Create equatorial grid (RA/Dec lines)
 */
function createEquatorialGrid() {
  const group = new THREE.Group();
  const material = new THREE.LineBasicMaterial({
    color: COLORS.EQUATORIAL,
    transparent: true,
    opacity: ALPHA.GRID
  });

  const segmentCount = 128; // Smooth curves
  
  // RA lines (meridians) - from pole to pole
  for (let i = 0; i < GRID_DIVISIONS; i++) {
    const ra = (i / GRID_DIVISIONS) * 360;
    const points = [];
    
    for (let j = 0; j <= segmentCount; j++) {
      const dec = -90 + (j / segmentCount) * 180;
      const raRad = ra * DEG_TO_RAD;
      const decRad = dec * DEG_TO_RAD;
      
      const x = SPHERE_RADIUS * Math.cos(decRad) * Math.cos(raRad);
      const y = SPHERE_RADIUS * Math.sin(decRad);
      const z = -SPHERE_RADIUS * Math.cos(decRad) * Math.sin(raRad);
      
      points.push(new THREE.Vector3(x, y, z));
    }
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    group.add(line);
  }
  
  // Dec lines (parallels) - circles parallel to equator
  for (let i = 1; i < GRID_DIVISIONS / 2; i++) {
    const dec = -90 + (i / (GRID_DIVISIONS / 2)) * 180;
    if (Math.abs(dec) < 1) continue; // Skip equator (drawn separately)
    
    const points = [];
    const decRad = dec * DEG_TO_RAD;
    const radius = SPHERE_RADIUS * Math.cos(decRad);
    const y = SPHERE_RADIUS * Math.sin(decRad);
    
    for (let j = 0; j <= segmentCount; j++) {
      const ra = (j / segmentCount) * 360;
      const raRad = ra * DEG_TO_RAD;
      
      const x = radius * Math.cos(raRad);
      const z = -radius * Math.sin(raRad);
      
      points.push(new THREE.Vector3(x, y, z));
    }
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    group.add(line);
  }
  
  return group;
}

/**
 * Create ecliptic grid (Lon/Lat lines)
 */
function createEclipticGrid() {
  const group = new THREE.Group();
  const material = new THREE.LineBasicMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: ALPHA.GRID
  });

  const segmentCount = 128;
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  
  // Longitude lines (meridians on ecliptic)
  for (let i = 0; i < GRID_DIVISIONS; i++) {
    const lon = (i / GRID_DIVISIONS) * 360;
    const points = [];
    
    for (let j = 0; j <= segmentCount; j++) {
      const lat = -90 + (j / segmentCount) * 180;
      const lonRad = lon * DEG_TO_RAD;
      const latRad = lat * DEG_TO_RAD;
      
      // Ecliptic coordinates to Cartesian
      const x = SPHERE_RADIUS * Math.cos(latRad) * Math.cos(lonRad);
      const y = SPHERE_RADIUS * Math.sin(latRad);
      const z = -SPHERE_RADIUS * Math.cos(latRad) * Math.sin(lonRad);
      
      // Rotate by obliquity to align with equatorial frame
      const yRot = y * Math.cos(obliquity) - z * Math.sin(obliquity);
      const zRot = y * Math.sin(obliquity) + z * Math.cos(obliquity);
      
      points.push(new THREE.Vector3(x, yRot, zRot));
    }
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    group.add(line);
  }
  
  // Latitude lines (parallels on ecliptic)
  for (let i = 1; i < GRID_DIVISIONS / 2; i++) {
    const lat = -90 + (i / (GRID_DIVISIONS / 2)) * 180;
    if (Math.abs(lat) < 1) continue; // Skip ecliptic plane (drawn separately)
    
    const points = [];
    const latRad = lat * DEG_TO_RAD;
    const radius = SPHERE_RADIUS * Math.cos(latRad);
    const yEcl = SPHERE_RADIUS * Math.sin(latRad);
    
    for (let j = 0; j <= segmentCount; j++) {
      const lon = (j / segmentCount) * 360;
      const lonRad = lon * DEG_TO_RAD;
      
      const x = radius * Math.cos(lonRad);
      const z = -radius * Math.sin(lonRad);
      
      // Rotate by obliquity
      const yRot = yEcl * Math.cos(obliquity) - z * Math.sin(obliquity);
      const zRot = yEcl * Math.sin(obliquity) + z * Math.cos(obliquity);
      
      points.push(new THREE.Vector3(x, yRot, zRot));
    }
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    group.add(line);
  }
  
  return group;
}
