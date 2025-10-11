/**
 * Arc rendering for all three coordinate systems
 */

import * as THREE from 'three';
import { 
  SPHERE_RADIUS, 
  COLORS, 
  ALPHA, 
  DEG_TO_RAD, 
  OBLIQUITY_J2000,
  ASHVINI_ECLIPTIC_LON,
  ARC_OFFSET
} from '../celestial/constants.js';
import { 
  sphericalToCartesian,
  projectOntoPlane,
  normalize,
  cross,
  greatCirclePlaneIntersection
} from '../celestial/SphereGeometry.js';
import { equatorialToEcliptic } from '../celestial/CoordinateCalculator.js';
import { createArcLabel } from './LabelRenderer.js';

/**
 * Create arc groups (initially empty)
 * @param {THREE.Scene} scene - Three.js scene
 * @returns {object} Object containing arc groups
 */
export function createArcs(scene) {
  const equatorialGroup = new THREE.Group();
  const eclipticGroup = new THREE.Group();
  const polarGroup = new THREE.Group();
  
  scene.add(equatorialGroup);
  scene.add(eclipticGroup);
  scene.add(polarGroup);
  
  return {
    equatorialGroup,
    eclipticGroup,
    polarGroup
  };
}

/**
 * Update all arcs based on star position
 * @param {object} arcs - Arc groups object
 * @param {object} starPosition - Star position {x, y, z}
 * @param {object} coords - Calculated coordinates
 * @param {boolean} showEquatorial - Show equatorial arcs
 * @param {boolean} showEcliptic - Show ecliptic arcs
 * @param {boolean} showPolar - Show polar arcs
 * @param {boolean} showLabels - Show arc value labels
 */
export function updateArcs(arcs, starPosition, coords, showEquatorial, showEcliptic, showPolar, showLabels) {
  // Clear existing arcs
  arcs.equatorialGroup.clear();
  arcs.eclipticGroup.clear();
  arcs.polarGroup.clear();
  
  // Render new arcs only if visible
  if (showEquatorial) {
    renderEquatorialArcs(arcs.equatorialGroup, starPosition, coords, showLabels);
  }
  if (showEcliptic) {
    renderEclipticArcs(arcs.eclipticGroup, starPosition, coords, showLabels);
  }
  if (showPolar) {
    renderPolarArcs(arcs.polarGroup, starPosition, coords, showLabels);
  }
}

/**
 * Render equatorial arcs (RA and Declination)
 */
function renderEquatorialArcs(group, starPosition, coords, showLabels) {
  const material = new THREE.LineBasicMaterial({
    color: COLORS.EQUATORIAL,
    transparent: true,
    opacity: 0.8
  });

  // Declination arc: S → Equator (perpendicular projection)
  const equatorNormal = { x: 0, y: 1, z: 0 };
  const projOnEquator = projectOntoPlane(starPosition, equatorNormal);
  
  // Normalize projection to sphere surface
  const len = Math.sqrt(projOnEquator.x ** 2 + projOnEquator.y ** 2 + projOnEquator.z ** 2);
  if (len > 0.01) {
    const normalizedProj = {
      x: (projOnEquator.x / len) * SPHERE_RADIUS,
      y: 0, // Force to equator
      z: (projOnEquator.z / len) * SPHERE_RADIUS
    };
    
    const decArc = createGreatCircleArc(starPosition, normalizedProj, material);
    group.add(decArc);
    
    // Add declination value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midDec = {
        x: (starPosition.x + normalizedProj.x) / 2,
        y: (starPosition.y + normalizedProj.y) / 2,
        z: (starPosition.z + normalizedProj.z) / 2
      };
      const decLabel = createArcLabel(`Dec: ${coords.dec.toFixed(1)}°`, midDec, '#4ade80');
      group.add(decLabel);
    }
    
    // RA arc: Eq (0°) → projection along equator (with offset)
    const vernalEquinox = { x: SPHERE_RADIUS, y: ARC_OFFSET, z: 0 };
    const offsetProj = { x: normalizedProj.x, y: ARC_OFFSET, z: normalizedProj.z };
    const raArc = createArcOnPlane(vernalEquinox, offsetProj, equatorNormal, material);
    group.add(raArc);
    
    // Add RA value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midRA = {
        x: (vernalEquinox.x + offsetProj.x) / 2,
        y: ARC_OFFSET,
        z: (vernalEquinox.z + offsetProj.z) / 2
      };
      const raLabel = createArcLabel(`RA: ${coords.ra.toFixed(2)}h`, midRA, '#4ade80');
      group.add(raLabel);
    }
  }
}

/**
 * Render ecliptic arcs (Longitude and Latitude)
 */
function renderEclipticArcs(group, starPosition, coords, showLabels) {
  const material = new THREE.LineBasicMaterial({
    color: COLORS.ECLIPTIC,
    transparent: true,
    opacity: 0.8
  });

  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  
  // Ecliptic plane normal (in equatorial frame)
  const eclipticNormal = {
    x: 0,
    y: Math.cos(obliquity),
    z: Math.sin(obliquity)
  };
  
  // Latitude arc: S → Ecliptic (perpendicular projection)
  const projOnEcliptic = projectOntoPlane(starPosition, eclipticNormal);
  
  const len = Math.sqrt(projOnEcliptic.x ** 2 + projOnEcliptic.y ** 2 + projOnEcliptic.z ** 2);
  if (len > 0.01) {
    const normalizedProj = {
      x: (projOnEcliptic.x / len) * SPHERE_RADIUS,
      y: (projOnEcliptic.y / len) * SPHERE_RADIUS,
      z: (projOnEcliptic.z / len) * SPHERE_RADIUS
    };
    
    const latArc = createGreatCircleArc(starPosition, normalizedProj, material);
    group.add(latArc);
    
    // Add latitude value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midLat = {
        x: (starPosition.x + normalizedProj.x) / 2,
        y: (starPosition.y + normalizedProj.y) / 2,
        z: (starPosition.z + normalizedProj.z) / 2
      };
      const latLabel = createArcLabel(`Lat: ${coords.lat.toFixed(1)}°`, midLat, '#60a5fa');
      group.add(latLabel);
    }
    
    // Longitude arc: Eq → projection along ecliptic (with offset)
    // Create offset vector perpendicular to ecliptic plane
    const offsetVec = {
      x: eclipticNormal.x * ARC_OFFSET,
      y: eclipticNormal.y * ARC_OFFSET,
      z: eclipticNormal.z * ARC_OFFSET
    };
    
    const vernalEquinox = { x: SPHERE_RADIUS + offsetVec.x, y: offsetVec.y, z: offsetVec.z };
    const offsetProj = {
      x: normalizedProj.x + offsetVec.x,
      y: normalizedProj.y + offsetVec.y,
      z: normalizedProj.z + offsetVec.z
    };
    
    const lonArc = createArcOnPlane(vernalEquinox, offsetProj, eclipticNormal, material);
    group.add(lonArc);
    
    // Add longitude value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midLon = {
        x: (vernalEquinox.x + offsetProj.x) / 2,
        y: (vernalEquinox.y + offsetProj.y) / 2,
        z: (vernalEquinox.z + offsetProj.z) / 2
      };
      const lonLabel = createArcLabel(`Lon: ${coords.lon.toFixed(1)}°`, midLon, '#60a5fa');
      group.add(lonLabel);
    }
  }
}

/**
 * Render polar arcs (Dhruvaka and Vikṣepa)
 */
function renderPolarArcs(group, starPosition, coords, showLabels) {
  const material = new THREE.LineBasicMaterial({
    color: COLORS.POLAR,
    transparent: true,
    opacity: 0.85
  });

  const pole = { x: 0, y: SPHERE_RADIUS, z: 0 };
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  
  // Ecliptic plane normal
  const eclipticNormal = {
    x: 0,
    y: Math.cos(obliquity),
    z: Math.sin(obliquity)
  };
  
  // Find intersection (Ec) of great circle through P and S with ecliptic
  const intersection = greatCirclePlaneIntersection(pole, starPosition, eclipticNormal);
  
  if (intersection) {
    // Vikṣepa arc: S → Ec
    const vikshepaArc = createGreatCircleArc(starPosition, intersection, material);
    group.add(vikshepaArc);
    
    // Add Vikṣepa value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midVik = {
        x: (starPosition.x + intersection.x) / 2,
        y: (starPosition.y + intersection.y) / 2,
        z: (starPosition.z + intersection.z) / 2
      };
      const vikLabel = createArcLabel(`Vikṣepa: ${coords.vikshepa.toFixed(1)}°`, midVik, '#fbbf24');
      group.add(vikLabel);
    }
    
    // Ashvini position (L′) at 34° on ecliptic
    const ashviniLonRad = ASHVINI_ECLIPTIC_LON * DEG_TO_RAD;
    const ashviniX = SPHERE_RADIUS * Math.cos(ashviniLonRad);
    const ashviniZ = -SPHERE_RADIUS * Math.sin(ashviniLonRad);
    const ashviniY = 0 * Math.cos(obliquity) - ashviniZ * Math.sin(obliquity);
    const ashviniZRot = 0 * Math.sin(obliquity) + ashviniZ * Math.cos(obliquity);
    
    const ashviniPos = { x: ashviniX, y: ashviniY, z: ashviniZRot };
    
    // Dhruvaka arc: Ec → L′ along ecliptic (with offset)
    const offsetVec = {
      x: eclipticNormal.x * ARC_OFFSET * 1.5,
      y: eclipticNormal.y * ARC_OFFSET * 1.5,
      z: eclipticNormal.z * ARC_OFFSET * 1.5
    };
    
    const offsetIntersection = {
      x: intersection.x + offsetVec.x,
      y: intersection.y + offsetVec.y,
      z: intersection.z + offsetVec.z
    };
    
    const offsetAshvini = {
      x: ashviniPos.x + offsetVec.x,
      y: ashviniPos.y + offsetVec.y,
      z: ashviniPos.z + offsetVec.z
    };
    
    const dhruvakaArc = createArcOnPlane(offsetIntersection, offsetAshvini, eclipticNormal, material);
    group.add(dhruvakaArc);
    
    // Add Dhruvaka value label at midpoint (only if labels are visible)
    if (showLabels) {
      const midDhr = {
        x: (offsetIntersection.x + offsetAshvini.x) / 2,
        y: (offsetIntersection.y + offsetAshvini.y) / 2,
        z: (offsetIntersection.z + offsetAshvini.z) / 2
      };
      const dhrLabel = createArcLabel(`Dhruvaka: ${coords.dhruvaka.toFixed(1)}°`, midDhr, '#fbbf24');
      group.add(dhrLabel);
    }
  }
}

/**
 * Create a great circle arc between two points
 * @param {object} p1 - Start point {x, y, z}
 * @param {object} p2 - End point {x, y, z}
 * @param {THREE.Material} material - Line material
 * @returns {THREE.Line} Arc line
 */
function createGreatCircleArc(p1, p2, material) {
  const points = [];
  const segmentCount = 64;
  
  // Normalize vectors
  const v1 = normalize(p1);
  const v2 = normalize(p2);
  
  // Find angle between vectors
  const dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
  const angle = Math.acos(Math.max(-1, Math.min(1, dot)));
  
  // Create arc using slerp
  for (let i = 0; i <= segmentCount; i++) {
    const t = i / segmentCount;
    const theta = t * angle;
    
    const sinTheta = Math.sin(theta);
    const sinAngle = Math.sin(angle);
    
    if (Math.abs(sinAngle) < 0.001) {
      // Points are too close, draw straight line
      points.push(new THREE.Vector3(
        p1.x + t * (p2.x - p1.x),
        p1.y + t * (p2.y - p1.y),
        p1.z + t * (p2.z - p1.z)
      ));
    } else {
      const a = Math.sin((1 - t) * angle) / sinAngle;
      const b = sinTheta / sinAngle;
      
      const x = a * v1.x + b * v2.x;
      const y = a * v1.y + b * v2.y;
      const z = a * v1.z + b * v2.z;
      
      points.push(new THREE.Vector3(x * SPHERE_RADIUS, y * SPHERE_RADIUS, z * SPHERE_RADIUS));
    }
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.Line(geometry, material);
}

/**
 * Create an arc on a plane between two points
 * @param {object} p1 - Start point {x, y, z}
 * @param {object} p2 - End point {x, y, z}
 * @param {object} planeNormal - Plane normal {x, y, z}
 * @param {THREE.Material} material - Line material
 * @returns {THREE.Line} Arc line
 */
function createArcOnPlane(p1, p2, planeNormal, material) {
  const points = [];
  const segmentCount = 64;
  
  // Project points onto plane (should already be on plane, but ensure)
  const proj1 = projectOntoPlane(p1, planeNormal);
  const proj2 = projectOntoPlane(p2, planeNormal);
  
  // Normalize to sphere surface
  const len1 = Math.sqrt(proj1.x ** 2 + proj1.y ** 2 + proj1.z ** 2);
  const len2 = Math.sqrt(proj2.x ** 2 + proj2.y ** 2 + proj2.z ** 2);
  
  if (len1 < 0.01 || len2 < 0.01) {
    return new THREE.Line(new THREE.BufferGeometry(), material);
  }
  
  const n1 = { x: proj1.x / len1, y: proj1.y / len1, z: proj1.z / len1 };
  const n2 = { x: proj2.x / len2, y: proj2.y / len2, z: proj2.z / len2 };
  
  // Find angle
  const dot = n1.x * n2.x + n1.y * n2.y + n1.z * n2.z;
  const angle = Math.acos(Math.max(-1, Math.min(1, dot)));
  
  // Slerp along plane
  for (let i = 0; i <= segmentCount; i++) {
    const t = i / segmentCount;
    const theta = t * angle;
    
    const sinAngle = Math.sin(angle);
    
    if (Math.abs(sinAngle) < 0.001) {
      points.push(new THREE.Vector3(
        proj1.x + t * (proj2.x - proj1.x),
        proj1.y + t * (proj2.y - proj1.y),
        proj1.z + t * (proj2.z - proj1.z)
      ));
    } else {
      const a = Math.sin((1 - t) * angle) / sinAngle;
      const b = Math.sin(theta) / sinAngle;
      
      const x = a * n1.x + b * n2.x;
      const y = a * n1.y + b * n2.y;
      const z = a * n1.z + b * n2.z;
      
      points.push(new THREE.Vector3(x * SPHERE_RADIUS, y * SPHERE_RADIUS, z * SPHERE_RADIUS));
    }
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.Line(geometry, material);
}
