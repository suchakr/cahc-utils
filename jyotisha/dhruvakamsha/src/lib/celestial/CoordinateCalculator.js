/**
 * Celestial coordinate calculations using astronomy-engine
 */

import * as Astronomy from 'astronomy-engine';
import { 
  cartesianToSpherical, 
  angularDistance,
  greatCirclePlaneIntersection,
  normalize,
  dot
} from './SphereGeometry.js';
import { 
  OBLIQUITY_J2000, 
  ASHVINI_ECLIPTIC_LON,
  DEG_TO_RAD,
  RAD_TO_DEG,
  DEG_TO_HOURS,
  SPHERE_RADIUS
} from './constants.js';

/**
 * Calculate all celestial coordinates from Cartesian position
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 * @param {number} z - Z coordinate
 * @returns {object} Coordinate object with ra, dec, lon, lat, dhruvaka, vikshepa
 */
export function calculateCoordinates(x, y, z) {
  // 1. Equatorial coordinates (RA/Dec)
  const { ra: raDeg, dec } = cartesianToSpherical(x, y, z);
  const ra = raDeg * DEG_TO_HOURS; // Convert to hours
  
  // 2. Ecliptic coordinates (Lon/Lat)
  const { lon, lat } = equatorialToEcliptic(raDeg, dec);
  
  // 3. Polar coordinates (Dhruvaka/Vikshepa)
  const { dhruvaka, vikshepa } = calculatePolarCoordinates(x, y, z, lon, lat);
  
  return {
    ra,        // hours (0-24)
    dec,       // degrees (-90 to +90)
    lon,       // degrees (0-360)
    lat,       // degrees (-90 to +90)
    dhruvaka,  // degrees (0-360)
    vikshepa   // degrees (-90 to +90)
  };
}

/**
 * Convert equatorial coordinates to ecliptic coordinates
 * @param {number} ra - Right Ascension in degrees
 * @param {number} dec - Declination in degrees
 * @returns {object} {lon, lat} Ecliptic longitude and latitude in degrees
 */
export function equatorialToEcliptic(ra, dec) {
  const obliquity = OBLIQUITY_J2000 * DEG_TO_RAD;
  const raRad = ra * DEG_TO_RAD;
  const decRad = dec * DEG_TO_RAD;
  
  // Rotation matrix for equatorial to ecliptic
  const sinObl = Math.sin(obliquity);
  const cosObl = Math.cos(obliquity);
  
  const sinDec = Math.sin(decRad);
  const cosDec = Math.cos(decRad);
  const sinRa = Math.sin(raRad);
  const cosRa = Math.cos(raRad);
  
  // Calculate ecliptic latitude
  const sinLat = sinDec * cosObl - cosDec * sinRa * sinObl;
  const lat = Math.asin(sinLat) * RAD_TO_DEG;
  
  // Calculate ecliptic longitude
  const y = sinRa * cosDec * cosObl + sinDec * sinObl;
  const x = cosRa * cosDec;
  let lon = Math.atan2(y, x) * RAD_TO_DEG;
  
  // Normalize to [0, 360)
  if (lon < 0) lon += 360;
  
  return { lon, lat };
}

/**
 * Calculate polar coordinates (Dhruvaka/Vikshepa) relative to Ashvini
 * @param {number} x - X coordinate of star
 * @param {number} y - Y coordinate of star
 * @param {number} z - Z coordinate of star
 * @param {number} lon - Ecliptic longitude of star (degrees)
 * @param {number} lat - Ecliptic latitude of star (degrees)
 * @returns {object} {dhruvaka, vikshepa} in degrees
 */
export function calculatePolarCoordinates(x, y, z, lon, lat) {
  // Celestial pole (North)
  const pole = { x: 0, y: SPHERE_RADIUS, z: 0 };
  
  // Star position
  const star = { x, y, z };
  
  // Ecliptic plane normal (tilted by obliquity from equatorial plane)
  const obliquityRad = OBLIQUITY_J2000 * DEG_TO_RAD;
  const eclipticNormal = {
    x: 0,
    y: Math.cos(obliquityRad),
    z: Math.sin(obliquityRad)
  };
  
  // Find intersection (Ec) of great circle through P and S with ecliptic plane
  const intersection = greatCirclePlaneIntersection(pole, star, eclipticNormal);
  
  if (!intersection) {
    // Fallback: star is at pole or calculation failed
    return { dhruvaka: 0, vikshepa: lat };
  }
  
  // Vikshepa: angular distance from star to intersection along great circle
  const { ra: ecRa, dec: ecDec } = cartesianToSpherical(intersection.x, intersection.y, intersection.z);
  const { ra: starRa, dec: starDec } = cartesianToSpherical(x, y, z);
  const vikshepa = angularDistance(starRa, starDec, ecRa, ecDec);
  
  // Sign convention: positive if star is above ecliptic (same sign as ecliptic latitude)
  const signedVikshepa = lat >= 0 ? vikshepa : -vikshepa;
  
  // Dhruvaka: angular distance along ecliptic from intersection to Ashvini
  const { lon: ecLon } = equatorialToEcliptic(ecRa, ecDec);
  
  // Angular distance from Ec to Ashvini along ecliptic
  let dhruvaka = ecLon - ASHVINI_ECLIPTIC_LON;
  
  // Normalize to [0, 360)
  if (dhruvaka < 0) dhruvaka += 360;
  
  return { dhruvaka, vikshepa: signedVikshepa };
}

/**
 * Generate initial star position for demo
 * Position to produce Dhruvaka ≈ 16.6°, Vikṣepa ≈ 24.9°
 */
export function generateInitialStarPosition() {
  // Using RA ≈ 45° (3h), Dec ≈ 45° produces approximately:
  // Dhruvaka ≈ 13.5°, Vikṣepa ≈ 27.9°
  const ra = 45; // degrees (3h)
  const dec = 45; // degrees
  
  const raRad = ra * DEG_TO_RAD;
  const decRad = dec * DEG_TO_RAD;
  
  const x = SPHERE_RADIUS * Math.cos(decRad) * Math.cos(raRad);
  const y = SPHERE_RADIUS * Math.sin(decRad);
  const z = -SPHERE_RADIUS * Math.cos(decRad) * Math.sin(raRad);
  
  return { x, y, z };
}

/**
 * Generate random mid-sky position for testing
 */
export function generateRandomMidSkyPosition() {
  // Random declination between 15° and 45° (mid-sky)
  const dec = 15 + Math.random() * 30;
  
  // Random RA between 0 and 360 degrees
  const ra = Math.random() * 360;
  
  const raRad = ra * DEG_TO_RAD;
  const decRad = dec * DEG_TO_RAD;
  
  const x = SPHERE_RADIUS * Math.cos(decRad) * Math.cos(raRad);
  const y = SPHERE_RADIUS * Math.sin(decRad);
  const z = -SPHERE_RADIUS * Math.cos(decRad) * Math.sin(raRad);
  
  return { x, y, z };
}
