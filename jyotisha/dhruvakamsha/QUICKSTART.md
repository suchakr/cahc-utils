# Quick Start Guide - Dhruvakamsha

## 🚀 Getting Started (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/sunder/projects/cahc/cahc-utils/jyotisha/dhruvakamsha
npm install
```

### 2. Start Development Server

```bash
npm run dev
# or
npx vite
```

The app will be available at: **http://localhost:5173/**

### 3. Using the App

#### Basic Interaction

1. **Rotate the View**
   - Click and drag anywhere on the black background
   - The entire celestial sphere rotates
   - Use mouse wheel to zoom in/out

2. **Move the Star**
   - Click and drag the yellow star
   - It will stay on the sphere surface
   - All coordinates update instantly

3. **Read Coordinates**
   - Look at the right panel (Value Pane)
   - Shows three coordinate systems:
     - **Equatorial** (green): RA and Dec
     - **Ecliptic** (blue): Longitude and Latitude
     - **Polar** (yellow): Dhruvaka and Vikṣepa

4. **Toggle Visibility**
   - Use the left panel (Control Panel)
   - Show/hide any element:
     - Grids (dotted lines)
     - Axes (solid circles)
     - Arcs (colored lines from star)
     - Labels and markers

#### Understanding the Visual Elements

**Colors**
- 🟢 Green = Equatorial system (RA/Dec)
- 🔵 Blue = Ecliptic system (Lon/Lat)
- 🟡 Yellow = Polar system (Dhruvaka/Vikṣepa)

**Markers (small spheres)**
- **Eq** (green/blue) = Vernal Equinox (0° RA, 0° Lon)
- **P** (green) = North Celestial Pole
- **P′** (blue) = North Ecliptic Pole
- **L′** (yellow) = Ashvini reference point (34° ecliptic longitude)

**Arcs (lines from star)**
- Green arcs show how RA/Dec are measured
- Blue arcs show how ecliptic Lon/Lat are measured
- Yellow arcs show Dhruvaka/Vikṣepa relative to Ashvini

### 4. Building for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

### 5. Deploying to Vercel

```bash
# Install Vercel CLI (first time only)
npm i -g vercel

# Deploy
vercel
```

Or simply drag the `dist/` folder to Vercel's web interface.

---

## 🎯 Key Concepts

### What is Dhruvaka and Vikṣepa?

This is a polar coordinate system based on traditional Indian astronomy:

- **Vikṣepa**: How far the star is from the ecliptic plane (similar to ecliptic latitude)
- **Dhruvaka**: Angular distance measured along the ecliptic from a reference point
- **Reference Point**: Ashvini (β Arietis), historically at 0°, now at 34° due to precession

### Why J2000?

J2000 is a standard epoch (January 1, 2000, 12:00 TT) used by modern astronomy to specify celestial coordinates. It accounts for the slow wobble of Earth's axis (precession).

### Coordinate System Relationships

All three systems describe the same point on the sphere:
1. **Equatorial**: Based on Earth's equator and rotation axis
2. **Ecliptic**: Based on Earth's orbital plane around the Sun
3. **Polar**: Based on the ecliptic with a traditional reference point

The ecliptic is tilted 23.439° from the equator, which is why you see that angle in the visualization.

---

## 🔧 Troubleshooting

**Server won't start?**
```bash
rm -rf node_modules package-lock.json
npm install
npx vite
```

**Browser shows blank screen?**
- Check browser console (F12) for errors
- Ensure you're using a modern browser (Chrome, Firefox, Safari, Edge)
- WebGL must be enabled

**Star won't drag?**
- Make sure "Star Position" is checked in the control panel
- Try clicking directly on the yellow sphere
- Cursor should change to a "grab" hand when hovering

**Coordinates seem wrong?**
- Remember: all coordinates are in J2000 epoch
- RA is in hours (0-24h), not degrees
- Dhruvaka is measured from Ashvini at 34°, not from vernal equinox

---

## 📚 Files You Might Want to Edit

**Change colors?**
- Edit: `src/styles/global.css` (CSS variables)
- Edit: `src/lib/celestial/constants.js` (Three.js colors)

**Adjust grid spacing?**
- Edit: `src/lib/celestial/constants.js` → `GRID_DIVISIONS`

**Change sphere size?**
- Edit: `src/lib/celestial/constants.js` → `SPHERE_RADIUS`

**Modify Ashvini reference?**
- Edit: `src/lib/celestial/constants.js` → `ASHVINI_ECLIPTIC_LON`

---

## 🎓 Learning Resources

- [Celestial Coordinate Systems](https://en.wikipedia.org/wiki/Celestial_coordinate_system)
- [J2000 Epoch](https://en.wikipedia.org/wiki/Epoch_(astronomy)#Julian_years_and_J2000)
- [Three.js Fundamentals](https://threejs.org/manual/)
- [Spherical Trigonometry](https://en.wikipedia.org/wiki/Spherical_trigonometry)

---

## ✅ Quick Test

Try these to verify everything works:

1. ✅ Drag star to North Pole → Dec should show ~90°
2. ✅ Drag star to equator → Dec should show ~0°
3. ✅ Look at Ashvini marker → Should be at ~34° on blue ecliptic
4. ✅ Toggle all checkboxes → Elements appear/disappear
5. ✅ Rotate sphere 360° → Should be smooth and responsive

---

**Need Help?** Check `IMPLEMENTATION.md` for technical details or `README.md` for full documentation.

Enjoy exploring the celestial sphere! 🌌✨
