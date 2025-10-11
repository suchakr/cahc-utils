import * as THREE from 'three';
import { SPHERE_RADIUS, DEG_TO_RAD, ECLIPTIC_POLE, COLORS } from '../celestial/constants.js';
import { sphericalToCartesian } from '../celestial/SphereGeometry.js';

/**
 * Creates great circle objects that will be dynamically updated
 */
export function createGreatCircles(scene) {
  const psCircle = new THREE.Group();
  const pPrimeCircle = new THREE.Group();
  
  psCircle.visible = false;
  pPrimeCircle.visible = false;
  
  scene.add(psCircle);
  scene.add(pPrimeCircle);
  
  return {
    psCircle,
    pPrimeCircle
  };
}

/**
 * Updates great circles based on star position
 * PS Circle: Green dashed circle through celestial pole (P) and star (S)
 * P'S Circle: Blue dashed circle through ecliptic pole (P') and star (S)
 */
export function updateGreatCircles(greatCircles, starPosition, showPSCircle, showPPrimeCircle) {
  const { psCircle, pPrimeCircle } = greatCircles;
  
  // Clear existing circles
  clearGroup(psCircle);
  clearGroup(pPrimeCircle);
  
  // Celestial pole position (0, SPHERE_RADIUS, 0)
  const polePosition = new THREE.Vector3(0, SPHERE_RADIUS, 0);
  
  // Ecliptic pole position (at ecliptic latitude 90°)
  // In equatorial coordinates: RA = 18h (270°), Dec = 90° - obliquity
  const raRad = ECLIPTIC_POLE.ra * DEG_TO_RAD;
  const decRad = ECLIPTIC_POLE.dec * DEG_TO_RAD;
  
  const pPrimePosition = new THREE.Vector3(
    SPHERE_RADIUS * Math.cos(decRad) * Math.cos(raRad),
    SPHERE_RADIUS * Math.sin(decRad),
    -SPHERE_RADIUS * Math.cos(decRad) * Math.sin(raRad)
  );
  
  // Star position
  const starPos = new THREE.Vector3(starPosition.x, starPosition.y, starPosition.z);
  
  // Create P-S great circle (green, dashed)
  if (showPSCircle) {
    const psCircleMesh = createGreatCircle(polePosition, starPos, COLORS.EQUATORIAL);
    psCircle.add(psCircleMesh);
    psCircle.visible = true;
  } else {
    psCircle.visible = false;
  }
  
  // Create P'-S great circle (blue, dashed)
  if (showPPrimeCircle) {
    const pPrimeCircleMesh = createGreatCircle(pPrimePosition, starPos, COLORS.ECLIPTIC);
    pPrimeCircle.add(pPrimeCircleMesh);
    pPrimeCircle.visible = true;
  } else {
    pPrimeCircle.visible = false;
  }
}

/**
 * Creates a full great circle passing through two points on the sphere
 */
function createGreatCircle(point1, point2, color) {
  // Normalize the input points
  const p1 = point1.clone().normalize();
  const p2 = point2.clone().normalize();
  
  // Find the normal to the plane containing the great circle
  const normal = new THREE.Vector3().crossVectors(p1, p2).normalize();
  
  // If points are antipodal or identical, return empty geometry
  if (normal.length() < 0.001) {
    return new THREE.Object3D();
  }
  
  // Create circle by rotating a point perpendicular to the normal
  const numSegments = 128;
  const points = [];
  
  // Find a vector perpendicular to the normal to start the circle
  let perpendicular;
  if (Math.abs(normal.x) < 0.9) {
    perpendicular = new THREE.Vector3(1, 0, 0).cross(normal).normalize();
  } else {
    perpendicular = new THREE.Vector3(0, 1, 0).cross(normal).normalize();
  }
  
  // Rotate the perpendicular vector around the normal to create circle
  for (let i = 0; i <= numSegments; i++) {
    const angle = (i / numSegments) * Math.PI * 2;
    const rotationMatrix = new THREE.Matrix4().makeRotationAxis(normal, angle);
    const point = perpendicular.clone().applyMatrix4(rotationMatrix);
    point.multiplyScalar(SPHERE_RADIUS);
    points.push(point);
  }
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineDashedMaterial({
    color: color,
    transparent: true,
    opacity: 0.7,
    dashSize: 0.5,
    gapSize: 0.3,
    scale: 0.5
  });
  
  const circle = new THREE.Line(geometry, material);
  circle.computeLineDistances(); // Required for dashed lines
  
  return circle;
}

/**
 * Helper function to clear all objects from a group
 */
function clearGroup(group) {
  while (group.children.length > 0) {
    const child = group.children[0];
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
    group.remove(child);
  }
}
