# Dhruvakamsha - Celestial Sphere Visualization

An interactive 3D web application for visualizing celestial coordinates and arcs on the celestial sphere. Supports equatorial (RA/Dec), ecliptic (Lon/Lat), and polar (Dhruvaka/Vikṣepa) coordinate systems with reference to Ashvini.

![Celestial Sphere Visualization](https://img.shields.io/badge/Three.js-Interactive_3D-blue)
![Svelte](https://img.shields.io/badge/Svelte-Framework-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Interactive 3D Celestial Sphere**: Rotate the sphere with mouse gestures to view from any angle
- **Three Coordinate Systems**:
  - Equatorial: Right Ascension (RA) and Declination (Dec)
  - Ecliptic: Longitude and Latitude
  - Polar: Dhruvaka and Vikṣepa (relative to Ashvini at 34° ecliptic longitude)
- **Draggable Star**: Position a star anywhere on the celestial sphere
- **Real-time Calculations**: All coordinates update dynamically as you drag the star
- **Visual Arcs**: See the geometric relationships between coordinate systems
- **Toggle Controls**: Show/hide grids, axes, arcs, and markers
- **J2000 Epoch**: All calculations reference the J2000 standard epoch

## 🚀 Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

```bash
# Navigate to the project directory
cd dhruvakamsha

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open in your browser at `http://localhost:3000`

### Building for Production

```bash
# Build the app
npm run build

# Preview the production build
npm run preview
```

The built files will be in the `dist/` directory, ready for deployment.

## 🎯 Usage

### Basic Interaction

1. **Rotate the View**: Click and drag on the background to rotate the celestial sphere
2. **Drag the Star**: Click and drag the yellow star to position it on the sphere
3. **View Coordinates**: The right panel shows all coordinate values in real-time
4. **Toggle Elements**: Use the left control panel to show/hide different elements

### Understanding the Display

#### Color Coding
- **Green**: Equatorial system (RA/Dec)
- **Blue**: Ecliptic system (Lon/Lat)
- **Yellow**: Polar system (Dhruvaka/Vikṣepa)

#### Key Markers
- **Eq**: Vernal Equinox (intersection of equator and ecliptic)
- **P**: Celestial Pole (north)
- **P′**: Ecliptic Pole
- **L′**: Ashvini reference point (34° ecliptic longitude)

#### Arcs
- **Equatorial Arcs** (green):
  - Declination: Star → Equator (perpendicular)
  - Right Ascension: Eq → Star's projection on equator
  
- **Ecliptic Arcs** (blue):
  - Latitude: Star → Ecliptic (perpendicular)
  - Longitude: Eq → Star's projection on ecliptic
  
- **Polar Arcs** (yellow):
  - Vikṣepa: Star → Intersection with ecliptic (through pole)
  - Dhruvaka: Intersection → Ashvini (along ecliptic)

## 📐 Coordinate Systems

### Equatorial Coordinates (J2000)
- **Right Ascension (RA)**: 0h to 24h, measured eastward from vernal equinox
- **Declination (Dec)**: -90° to +90°, positive north of equator

### Ecliptic Coordinates (J2000)
- **Longitude**: 0° to 360°, measured eastward from vernal equinox along ecliptic
- **Latitude**: -90° to +90°, positive north of ecliptic plane
- **Obliquity**: 23.439° (J2000 epoch)

### Polar Coordinates (Ashvini Reference)
- **Dhruvaka**: Angular distance along ecliptic from intersection point to Ashvini (34°)
- **Vikṣepa**: Angular distance from star to ecliptic along great circle through pole
- **Historical Context**: Ashvini was at 0° in ancient systems; now at 34° in J2000

## 🏗️ Project Structure

```
dhruvakamsha/
├── src/
│   ├── App.svelte                    # Root component
│   ├── main.js                       # Entry point
│   ├── styles/
│   │   └── global.css                # Global styles
│   ├── lib/
│   │   ├── celestial/
│   │   │   ├── constants.js          # Astronomical constants
│   │   │   ├── SphereGeometry.js     # Spherical math utilities
│   │   │   └── CoordinateCalculator.js  # Coordinate transformations
│   │   ├── three/
│   │   │   ├── SphereCanvas.svelte   # Main 3D scene
│   │   │   ├── GridRenderer.js       # Grid rendering
│   │   │   ├── AxisRenderer.js       # Equator/ecliptic rendering
│   │   │   ├── MarkerRenderer.js     # Key point markers
│   │   │   ├── StarController.js     # Draggable star logic
│   │   │   └── ArcRenderer.js        # Arc rendering
│   │   └── components/
│   │       ├── ControlPanel.svelte   # Toggle controls
│   │       └── ValuePane.svelte      # Coordinate display
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

## 🔧 Technology Stack

- **Svelte 4**: Reactive UI framework
- **Three.js**: 3D rendering and WebGL
- **astronomy-engine**: Celestial coordinate calculations
- **Vite**: Build tool and dev server

## 📚 References

### Astronomical Concepts
- [IAU SOFA](http://www.iausofa.org/): Standards for Fundamental Astronomy
- [J2000 Epoch](https://en.wikipedia.org/wiki/Epoch_(astronomy)#Julian_years_and_J2000): Standard epoch for celestial coordinates
- [Celestial Coordinate Systems](https://en.wikipedia.org/wiki/Celestial_coordinate_system): Overview of systems

### Libraries
- [Three.js Documentation](https://threejs.org/docs/)
- [astronomy-engine](https://github.com/cosinekitty/astronomy): JavaScript astronomy library
- [Svelte Documentation](https://svelte.dev/docs)

## 🚢 Deployment

### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### GitHub Pages
```bash
# Build the project
npm run build

# Copy dist/ contents to your GitHub Pages repository
```

### Manual Deployment
Simply copy the contents of the `dist/` folder to any static hosting service.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built for pedagogical astronomy visualization
- Inspired by traditional Indian astronomical systems
- Uses J2000 epoch for consistency with modern astronomical data

## 📧 Contact

For questions or feedback, please open an issue on the repository.

---

**Enjoy exploring the celestial sphere! 🌌**
