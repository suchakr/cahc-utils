<script>
  export let coordinates;
  export let camera = { azimuth: 0, elevation: 0, distance: 0 };
  
  let isOpen = false;
  
  function togglePanel() {
    isOpen = !isOpen;
  }
  
  // Format RA as hours:minutes:seconds
  function formatRA(hours) {
    const h = Math.floor(hours);
    const m = Math.floor((hours - h) * 60);
    const s = Math.floor(((hours - h) * 60 - m) * 60);
    return `${String(h).padStart(2, '0')}h ${String(m).padStart(2, '0')}m ${String(s).padStart(2, '0')}s`;
  }
  
  // Format angle as degrees:arcminutes:arcseconds
  function formatDMS(degrees) {
    const sign = degrees < 0 ? '-' : '+';
    const absDeg = Math.abs(degrees);
    const d = Math.floor(absDeg);
    const m = Math.floor((absDeg - d) * 60);
    const s = Math.floor(((absDeg - d) * 60 - m) * 60);
    return `${sign}${String(d).padStart(2, '0')}° ${String(m).padStart(2, '0')}′ ${String(s).padStart(2, '0')}″`;
  }
  
  // Format longitude (0-360)
  function formatLon(degrees) {
    const d = Math.floor(degrees);
    const m = Math.floor((degrees - d) * 60);
    const s = Math.floor(((degrees - d) * 60 - m) * 60);
    return `${String(d).padStart(3, '0')}° ${String(m).padStart(2, '0')}′ ${String(s).padStart(2, '0')}″`;
  }
</script>

<!-- Mobile toggle button -->
<button class="mobile-toggle" on:click={togglePanel} aria-label="Toggle coordinates">
  <span class="info-icon">ℹ</span>
</button>

<!-- Backdrop for mobile -->
{#if isOpen}
  <div class="backdrop" on:click={togglePanel}></div>
{/if}

<aside class="value-pane" class:open={isOpen}>
  <h2>Coordinates</h2>
  
  <section class="equatorial-section">
    <h3>Equatorial (J2000)</h3>
    <div class="coord">
      <span class="label">RA:</span>
      <span class="value">{formatRA(coordinates.ra)}</span>
    </div>
    <div class="coord">
      <span class="label">Dec:</span>
      <span class="value">{formatDMS(coordinates.dec)}</span>
    </div>
  </section>
  
  <section class="ecliptic-section">
    <h3>Ecliptic (J2000)</h3>
    <div class="coord">
      <span class="label">Lon:</span>
      <span class="value">{formatLon(coordinates.lon)}</span>
    </div>
    <div class="coord">
      <span class="label">Lat:</span>
      <span class="value">{formatDMS(coordinates.lat)}</span>
    </div>
  </section>
  
  <section class="polar-section">
    <h3>Polar (wrt Ashvini)</h3>
    <div class="coord">
      <span class="label">Dhruvaka:</span>
      <span class="value">{formatLon(coordinates.dhruvaka)}</span>
    </div>
    <div class="coord">
      <span class="label">Vikṣepa:</span>
      <span class="value">{formatDMS(coordinates.vikshepa)}</span>
    </div>
  </section>
  
  <section class="camera-section">
    <h3>Camera View</h3>
    <div class="coord">
      <span class="label">Azimuth:</span>
      <span class="value">{camera.azimuth.toFixed(1)}°</span>
    </div>
    <div class="coord">
      <span class="label">Elevation:</span>
      <span class="value">{camera.elevation.toFixed(1)}°</span>
    </div>
    <div class="coord">
      <span class="label">Distance:</span>
      <span class="value">{camera.distance.toFixed(1)}</span>
    </div>
  </section>
</aside>

<style>
  .value-pane {
    position: absolute;
    top: 20px;
    right: 20px;
    background: var(--color-panel-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 16px;
    min-width: 280px;
    backdrop-filter: blur(10px);
    z-index: 10;
  }
  
  h2 {
    font-size: 20px;
    margin-bottom: 16px;
    color: #fff;
  }
  
  h3 {
    font-size: 14px;
    margin-bottom: 8px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  section {
    margin-bottom: 16px;
    padding: 12px;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.3);
  }
  
  section:last-child {
    margin-bottom: 0;
  }
  
  .equatorial-section {
    border-left: 3px solid var(--color-equatorial);
  }
  
  .ecliptic-section {
    border-left: 3px solid var(--color-ecliptic);
  }
  
  .polar-section {
    border-left: 3px solid var(--color-polar);
  }
  
  .camera-section {
    border-left: 3px solid #888;
  }
  
  .coord {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 15px;
  }
  
  .coord:last-child {
    margin-bottom: 0;
  }
  
  .label {
    color: #aaa;
    font-weight: 500;
  }
  
  .value {
    color: #fff;
    font-family: 'Courier New', monospace;
  }
  
  /* Mobile toggle button */
  .mobile-toggle {
    display: none;
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 100;
    background: var(--color-panel-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    width: 48px;
    height: 48px;
    cursor: pointer;
    backdrop-filter: blur(10px);
    padding: 0;
    align-items: center;
    justify-content: center;
  }
  
  .info-icon {
    font-size: 24px;
    color: #fff;
    font-weight: bold;
  }
  
  .backdrop {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9;
  }
  
  /* Mobile responsive styles */
  @media (max-width: 768px) {
    .mobile-toggle {
      display: flex;
    }
    
    .backdrop {
      display: block;
    }
    
    .value-pane {
      position: fixed;
      top: 80px;
      right: -320px;
      max-height: calc(100vh - 100px);
      overflow-y: auto;
      transition: right 0.3s ease-in-out;
      box-shadow: -4px 0 12px rgba(0, 0, 0, 0.3);
    }
    
    .value-pane.open {
      right: 20px;
    }
  }
</style>
