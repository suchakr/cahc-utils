<script>
  import SphereCanvas from './lib/three/SphereCanvas.svelte';
  import ControlPanel from './lib/components/ControlPanel.svelte';
  import ValuePane from './lib/components/ValuePane.svelte';
  import Legend from './lib/components/Legend.svelte';
  import Title from './lib/components/Title.svelte';

  // Visibility toggles
  let showEquatorialGrid = false;
  let showEclipticGrid = false;
  let showEquator = true;
  let showEcliptic = true;
  let showEclipticBand = false;
  let showNakshatras = false;
  let showMarkers = true;
  let showStar = true;
  let showEquatorialArcs = false;
  let showEclipticArcs = false;
  let showPolarArcs = true;
  let showArcLabels = true;
  let showNakshatraLabels = false;
  let showPSCircle = true;
  let showPPrimeCircle = false;

  // Coordinate values
  let coordinates = {
    ra: 0,      // hours
    dec: 0,     // degrees
    lon: 0,     // degrees
    lat: 0,     // degrees
    dhruvaka: 0,   // degrees
    vikshepa: 0    // degrees
  };
  
  // Camera angle values
  let camera = {
    azimuth: 0,   // degrees
    elevation: 0, // degrees
    distance: 0   // units
  };

  function handleCoordinateUpdate(event) {
    coordinates = event.detail;
  }
  
  function handleCameraUpdate(event) {
    camera = event.detail;
  }
</script>

<Title />

<main>
  <SphereCanvas
    {showEquatorialGrid}
    {showEclipticGrid}
    {showEquator}
    {showEcliptic}
    {showEclipticBand}
    {showNakshatras}
    {showMarkers}
    {showStar}
    {showEquatorialArcs}
    {showEclipticArcs}
    {showPolarArcs}
    {showArcLabels}
    {showNakshatraLabels}
    {showPSCircle}
    {showPPrimeCircle}
    on:coordinateUpdate={handleCoordinateUpdate}
    on:cameraUpdate={handleCameraUpdate}
  />
  
  <ControlPanel
    bind:showEquatorialGrid
    bind:showEclipticGrid
    bind:showEquator
    bind:showEcliptic
    bind:showEclipticBand
    bind:showNakshatras
    bind:showMarkers
    bind:showStar
    bind:showEquatorialArcs
    bind:showEclipticArcs
    bind:showPolarArcs
    bind:showArcLabels
    bind:showNakshatraLabels
    bind:showPSCircle
    bind:showPPrimeCircle
  />
  
  <ValuePane {coordinates} {camera} />
  
  <Legend />
</main>

<style>
  main {
    width: 100%;
    height: 100%;
    position: relative;
    flex: 1;
  }
</style>
