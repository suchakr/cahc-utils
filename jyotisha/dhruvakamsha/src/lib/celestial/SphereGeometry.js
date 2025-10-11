/**
 * Spherical geometry utilities for celestial coordinate transformations
 */

import { DEG_TO_RAD, RAD_TO_DEG, SPHERE_RADIUS } from './constants.js';

/**
 * Convert spherical coordinates (RA, Dec) to Cartesian (x, y, z)
 * @param {number} ra - Right Ascension in degrees
 * @param {number} dec - Declination in degrees
 * @param {number} radius - Sphere radius (default: SPHERE_RADIUS)
 * @returns {object} {x, y, z} Cartesian coordinates
 */
export function sphericalToCartesian(ra, dec, radius = SPHERE_RADIUS) {
  const raRad = ra * DEG_TO_RAD;
  const decRad = dec * DEG_TO_RAD;
  
  // Three.js coordinate system: Y-up
  // RA increases counterclockwise from +X axis when viewed from +Y
  // Dec: 0° at equator, +90° at north pole (+Y)
  const x = radius * Math.cos(decRad) * Math.cos(raRad);
  const y = radius * Math.sin(decRad);
  const z = -radius * Math.cos(decRad) * Math.sin(raRad);
  
  return { x, y, z };
}

/**
 * Convert Cartesian (x, y, z) to spherical (RA, Dec)
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 * @param {number} z - Z coordinate
 * @returns {object} {ra, dec} in degrees
 */
export function cartesianToSpherical(x, y, z) {
  const radius = Math.sqrt(x * x + y * y + z * z);
  const dec = Math.asin(y / radius) * RAD_TO_DEG;
  let ra = Math.atan2(-z, x) * RAD_TO_DEG;
  
  // Normalize RA to [0, 360)
  if (ra < 0) ra += 360;
  
  return { ra, dec };
}

/**
 * Convert ecliptic coordinates (lon, lat) to Cartesian
 * @param {number} lon - Ecliptic longitude in degrees
 * @param {number} lat - Ecliptic latitude in degrees
 * @param {number} radius - Sphere radius
 * @returns {object} {x, y, z} Cartesian coordinates
 */
export function eclipticToCartesian(lon, lat, radius = SPHERE_RADIUS) {
  const lonRad = lon * DEG_TO_RAD;
  const latRad = lat * DEG_TO_RAD;
  
  const x = radius * Math.cos(latRad) * Math.cos(lonRad);
  const y = radius * Math.sin(latRad);
  const z = -radius * Math.cos(latRad) * Math.sin(lonRad);
  
  return { x, y, z };
}

/**
 * Calculate angular distance between two points on a sphere
 * @param {number} ra1 - RA of point 1 (degrees)
 * @param {number} dec1 - Dec of point 1 (degrees)
 * @param {number} ra2 - RA of point 2 (degrees)
 * @param {number} dec2 - Dec of point 2 (degrees)
 * @returns {number} Angular distance in degrees
 */
export function angularDistance(ra1, dec1, ra2, dec2) {
  const ra1Rad = ra1 * DEG_TO_RAD;
  const dec1Rad = dec1 * DEG_TO_RAD;
  const ra2Rad = ra2 * DEG_TO_RAD;
  const dec2Rad = dec2 * DEG_TO_RAD;
  
  // Haversine formula
  const deltaRa = ra2Rad - ra1Rad;
  const deltaDec = dec2Rad - dec1Rad;
  
  const a = Math.sin(deltaDec / 2) ** 2 +
            Math.cos(dec1Rad) * Math.cos(dec2Rad) * Math.sin(deltaRa / 2) ** 2;
  const c = 2 * Math.asin(Math.sqrt(a));
  
  return c * RAD_TO_DEG;
}

/**
 * Normalize a 3D vector
 * @param {object} v - Vector {x, y, z}
 * @returns {object} Normalized vector
 */
export function normalize(v) {
  const len = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
  if (len === 0) return { x: 0, y: 0, z: 0 };
  return { x: v.x / len, y: v.y / len, z: v.z / len };
}

/**
 * Dot product of two 3D vectors
 * @param {object} v1 - Vector {x, y, z}
 * @param {object} v2 - Vector {x, y, z}
 * @returns {number} Dot product
 */
export function dot(v1, v2) {
  return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
}

/**
 * Cross product of two 3D vectors
 * @param {object} v1 - Vector {x, y, z}
 * @param {object} v2 - Vector {x, y, z}
 * @returns {object} Cross product vector
 */
export function cross(v1, v2) {
  return {
    x: v1.y * v2.z - v1.z * v2.y,
    y: v1.z * v2.x - v1.x * v2.z,
    z: v1.x * v2.y - v1.y * v2.x
  };
}

/**
 * Project a point onto a plane defined by its normal
 * @param {object} point - Point to project {x, y, z}
 * @param {object} planeNormal - Plane normal vector {x, y, z}
 * @returns {object} Projected point {x, y, z}
 */
export function projectOntoPlane(point, planeNormal) {
  const normal = normalize(planeNormal);
  const distance = dot(point, normal);
  
  return {
    x: point.x - distance * normal.x,
    y: point.y - distance * normal.y,
    z: point.z - distance * normal.z
  };
}

/**
 * Find intersection of a great circle (through p1 and p2) with a plane
 * @param {object} p1 - Point 1 on great circle {x, y, z}
 * @param {object} p2 - Point 2 on great circle {x, y, z}
 * @param {object} planeNormal - Normal to plane {x, y, z}
 * @returns {object|null} Intersection point {x, y, z} or null if no intersection
 */
export function greatCirclePlaneIntersection(p1, p2, planeNormal) {
  // Great circle is defined by the plane through origin, p1, and p2
  // Its normal is p1 × p2
  const gcNormal = cross(p1, p2);
  
  // Intersection line of two planes is perpendicular to both normals
  const intersectionDir = cross(gcNormal, planeNormal);
  
  const len = Math.sqrt(intersectionDir.x ** 2 + intersectionDir.y ** 2 + intersectionDir.z ** 2);
  if (len < 1e-10) return null; // Parallel planes
  
  // Normalize and scale to sphere radius
  return {
    x: (intersectionDir.x / len) * SPHERE_RADIUS,
    y: (intersectionDir.y / len) * SPHERE_RADIUS,
    z: (intersectionDir.z / len) * SPHERE_RADIUS
  };
}
