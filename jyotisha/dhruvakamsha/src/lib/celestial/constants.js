/**
 * Celestial coordinate constants for J2000 epoch
 */

// J2000 epoch (January 1, 2000, 12:00 TT)
export const J2000_EPOCH = 2451545.0; // Julian Date

// Obliquity of the ecliptic at J2000 (angle between equator and ecliptic)
export const OBLIQUITY_J2000 = 23.439281; // degrees

// Ashvini reference point (β Arietis / Sheratan)
// In J2000, Ashvini is at ~34° ecliptic longitude
export const ASHVINI_ECLIPTIC_LON = 34.0; // degrees

// Conversion constants
export const DEG_TO_RAD = Math.PI / 180;
export const RAD_TO_DEG = 180 / Math.PI;
export const HOURS_TO_DEG = 15; // 1 hour = 15 degrees
export const DEG_TO_HOURS = 1 / 15; // 1 degree = 1/15 hours

// Sphere rendering constants
export const SPHERE_RADIUS = 10; // arbitrary units
export const GRID_DIVISIONS = 24; // 24 divisions = 15° spacing
export const MARKER_SIZE = 0.15;
export const STAR_SIZE = 0.2;
// Arc offset to separate arcs from underlying circles
export const ARC_OFFSET = 0.15;

// Ecliptic pole position (at ecliptic latitude 90°)
// P′ is at ecliptic latitude 90°, ecliptic longitude can be any value (we use 0°)
// In equatorial coordinates: RA = 18h (270°), Dec = 90° - obliquity
export const ECLIPTIC_POLE = {
  ra: 270, // degrees (18 hours)
  dec: 90 - OBLIQUITY_J2000 // degrees = 66.561°
};

// Colors (matching CSS variables)
export const COLORS = {
  EQUATORIAL: 0x4ade80,   // green
  ECLIPTIC: 0x60a5fa,     // blue
  POLAR: 0xfbbf24,        // yellow/amber
  STAR: 0xfef3c7,         // pale yellow
  MARKER: 0xffffff        // white
};

// Alpha/opacity values
export const ALPHA = {
  GRID: 0.3,
  AXIS: 0.8,
  ARC: 0.9,
  MARKER: 1.0
};
