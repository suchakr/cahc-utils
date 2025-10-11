# Dhruvakamsha Visualization Web App - Requirements

## 🎯 Purpose
An interactive, pedagogic 3D web app to visualize celestial coordinates and arcs for a single star on the celestial sphere. Supports:
- Polar (Dhruvaka/Vikṣepa)
- Ecliptic Longitude/Latitude
- Equatorial Right Ascension/Declination

Designed for clarity, gesture-based interaction, and traditional astronomical alignment (e.g., Ashvini reference).

---

## 🧱 Tech Stack

| Layer         | Technology        | Notes |
|---------------|-------------------|-------|
| 3D Rendering  | Three.js          | Lightweight, gesture-friendly |
| UI Framework  | Svelte or React   | Reactive toggles and controls |
| Geometry      | gl-matrix or custom | Spherical transforms |
| Deployment    | GitHub Pages / Vercel | No backend needed |
| Backend       | None (Node.js optional for future) | Stateless frontend only |

---

## 🌌 Celestial Sphere Design

### 🧭 Coordinate Systems
- **Reference Epoch**: J2000
- **Equatorial Grid**: RA/Declination
- **Ecliptic Grid**: Longitude/Latitude
- **Polar Arcs**: Dhruvaka/Vikṣepa, measured wrt Ashvini (β Ari ~ 34° Ecliptic Long)

### 🧊 Sphere & Cube
- Render celestial sphere inside a rotatable cube
- Mouse gestures allow full 3D rotation

### 🟢🔵 Grid & Axes
- **Equatorial Grid**: Green dotted lines, mid-low alpha
- **Ecliptic Grid**: Blue dotted lines, mid-low alpha
- **Equator**: Solid green arc
- **Ecliptic**: Solid blue arc

### 📍 Key Markers
- **Vernal Equinox (Eq)**: Green/blue dot at RA = 0°, Ecliptic Long = 0°
- **Celestial Pole (P)**: Green dot
- **Ecliptic Pole (P′)**: Blue dot
- **Ashvini (L′)**: Marked at ~34° Ecliptic Longitude

---

## ⭐ Star Interaction

### 🟡 Star (S)
- One draggable star placed mid-sky at launch
- Drag updates all coordinate values and arcs dynamically

### 🧮 Coordinate Display
- Auto-computed RA/Decl, Ecliptic Lat/Lon, Dhruvaka/Vikṣepa
- If auto-computation fails, fallback to Alt/Az input (degrees)

---

## 🌀 Arc Visualization

---

## 🌌 Celestial Sphere Design

### 🧭 Coordinate Systems
- **Reference Epoch**: J2000
- **Equatorial Grid**: RA/Declination
- **Ecliptic Grid**: Longitude/Latitude
- **Polar Arcs**: Dhruvaka/Vikṣepa, measured wrt Ashvini (β Ari ~ 34° Ecliptic Long)

### 🧊 Sphere & Cube
- Render celestial sphere inside a rotatable cube
- Mouse gestures allow full 3D rotation

### 🟢🔵 Grid & Axes
- **Equatorial Grid**: Green dotted lines, mid-low alpha
- **Ecliptic Grid**: Blue dotted lines, mid-low alpha
- **Equator**: Solid green arc
- **Ecliptic**: Solid blue arc

### 📍 Key Markers
- **Vernal Equinox (Eq)**: Green/blue dot at RA = 0°, Ecliptic Long = 0°
- **Celestial Pole (P)**: Green dot
- **Ecliptic Pole (P′)**: Blue dot
- **Ashvini (L′)**: Marked at ~34° Ecliptic Longitude

---

## ⭐ Star Interaction

### 🟡 Star (S)
- One draggable star placed mid-sky at launch
- Drag updates all coordinate values and arcs dynamically

### 🧮 Coordinate Display
- Auto-computed RA/Decl, Ecliptic Lat/Lon, Dhruvaka/Vikṣepa
- If auto-computation fails, fallback to Alt/Az input (degrees)

---

## 🌀 Arc Visualization

### 🔁 Polar Arcs (Dhruvaka/Vikṣepa)
- Construct a great circle through:
  - **P** (Celestial Pole)
  - **S** (Star)
- Let this intersect the **Ecliptic** at point **Ec**
- Define:
  - **Arc(S → Ec)** = Vikṣepa
  - **Arc(Ec → L′)** = Dhruvaka (measured from Ec to Ashvini, L′ ≈ 34° Ecliptic Longitude)
- Rendered in **yellow**, visually distinct
- Arc values shown inline or in reserved canvas pane

### 🔵 Ecliptic Arcs (Longitude/Latitude)
- From **S**, drop perpendicular to the **Ecliptic plane**
- Define:
  - **Arc(S → Ecliptic)** = Ecliptic Latitude (±)
  - **Arc(Eq → projection of S on Ecliptic)** = Ecliptic Longitude (from Eq to projection, increasing eastward)
- Render arcs in **blue**
- Display values in degrees (J2000)

### 🟢 Equatorial Arcs (RA/Declination)
- From **S**, drop perpendicular to the **Equator**
- Define:
  - **Arc(S → Equator)** = Declination (±)
  - **Arc(Eq → projection of S on Equator)** = Right Ascension (from Eq to projection, increasing eastward)
- Render arcs in **green**
- Display values in hours (RA) and degrees (Decl), J2000

---

## 📦 Suggested Modular Architecture

### 1. `SphereCanvas`  
**Purpose**: Renders the celestial sphere inside a rotatable cube  
**Responsibilities**:
- Initialize Three.js scene, camera, lighting
- Handle mouse gestures for rotation
- Render sphere, grids, equator/ecliptic arcs

---

### 2. `GridRenderer`  
**Purpose**: Draws equatorial and ecliptic grids  
**Responsibilities**:
- Dotted lines with mid-low alpha
- Color-coded: green (equatorial), blue (ecliptic)
- Toggle visibility via props/state

---

### 3. `AxisRenderer`  
**Purpose**: Renders equator and ecliptic arcs  
**Responsibilities**:
- Solid arcs in respective colors
- Accurate placement using spherical geometry

---

### 4. `MarkerRenderer`  
**Purpose**: Places key celestial markers  
**Markers**:
- Eq (Vernal Equinox): green/blue dot
- P (Celestial Pole): green dot
- P′ (Ecliptic Pole): blue dot
- L′ (Ashvini): blue dot at ~34° Ecliptic Longitude

---

### 5. `StarController`  
**Purpose**: Manages draggable star (S)  
**Responsibilities**:
- Initialize star at mid-sky
- Enable dragging on sphere surface
- Trigger coordinate and arc updates

---

### 6. `CoordinateCalculator`  
**Purpose**: Computes celestial coordinates from star position  
**Outputs**:
- RA/Decl (Equatorial)
- Lon/Lat (Ecliptic)
- Dhruvaka/Vikṣepa (Polar, wrt Ashvini)

---

### 7. `ArcRenderer`  
**Purpose**: Draws coordinate arcs from star  
**Types**:
- Polar: S → Ec (Vikṣepa), Ec → L′ (Dhruvaka), yellow
- Ecliptic: S → Ecliptic (Lat), Eq → proj(S) (Lon), blue
- Equatorial: S → Equator (Decl), Eq → proj(S) (RA), green  
**Features**:
- Arcs follow great circles
- Values shown inline or in reserved pane

---

### 8. `ControlPanel`  
**Purpose**: UI for toggling visibility  
**Controls**:
- Equatorial Grid
- Ecliptic Grid
- Equator
- Ecliptic
- Star (S)
- Coordinate Labels
- Arc Types (Polar, Ecliptic, Equatorial)

---

### 9. `ValuePane`  
**Purpose**: Displays coordinate and arc values  
**Features**:
- RA (hours), Decl (degrees)
- Lon/Lat (degrees)
- Dhruvaka/Vikṣepa (degrees)
- Auto-updates on star drag

---

### 10. `DebugOverlay` (Optional)  
**Purpose**: Developer diagnostics  
**Features**:
- Raw spherical coordinates
- Cartesian vectors
- Arc lengths in radians/degrees

---

## 🧪 Testing & Validation ( Memo for humans)

### ✅ Coordinate Accuracy
- Cross-check RA/Decl, Lon/Lat, Dhruvaka/Vikṣepa using:
  - [Astropy](https://www.astropy.org/)
  - [Skyfield](https://rhodesmill.org/skyfield/)
  - Known stars (e.g., β Ari, Sirius, Polaris)

### 🧪 Visual Validation
- Confirm:
  - Arcs lie on correct great circles
  - Projections fall on correct planes
  - Eq, P, P′, L′ are correctly placed

### 🖱 Interaction Testing
- Ensure:
  - Star dragging updates all arcs and values
  - Mouse gestures rotate sphere smoothly
  - Toggle buttons work as expected

### 📏 UI Layout
- Check:
  - Arc labels do not overlap
  - Reserved pane displays values clearly
  - Colors and alpha levels are harmonious

---

## 📦 Future Extensions

- Epoch selector (e.g., J2000 vs current)
- Multiple stars and comparative arcs
- Guided walkthrough mode
- Export coordinates or snapshots

