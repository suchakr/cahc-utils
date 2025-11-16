<script>
  export let showEquatorialGrid;
  export let showEclipticGrid;
  export let showEquator;
  export let showEcliptic;
  export let showEclipticBand;
  export let showNakshatras;
  export let showMarkers;
  export let showStar;
  export let showEquatorialArcs;
  export let showEclipticArcs;
  export let showPolarArcs;
  export let showArcLabels;
  export let showNakshatraLabels;
  export let showPSCircle;
  export let showPPrimeCircle;
  
  let isOpen = false;
  
  function togglePanel() {
    isOpen = !isOpen;
  }
</script>

<!-- Mobile toggle button -->
<button class="mobile-toggle" on:click={togglePanel} aria-label="Toggle controls">
  <span class="hamburger-icon">
    <span></span>
    <span></span>
    <span></span>
  </span>
</button>

<!-- Backdrop for mobile -->
{#if isOpen}
  <div class="backdrop" on:click={togglePanel}></div>
{/if}

<aside class="control-panel" class:open={isOpen}>
  <h2>Controls</h2>
  
  <section>
    <h3>Grids</h3>
    <label>
      <input type="checkbox" bind:checked={showEquatorialGrid} />
      <span class="equatorial">Equatorial Grid</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showEclipticGrid} />
      <span class="ecliptic">Ecliptic Grid</span>
    </label>
  </section>
  
  <section>
    <h3>Axes</h3>
    <label>
      <input type="checkbox" bind:checked={showEquator} />
      <span class="equatorial">Equator</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showEcliptic} />
      <span class="ecliptic">Ecliptic</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showEclipticBand} />
      <span class="ecliptic">Ecliptic Band (±23.5°)</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showNakshatras} />
      <span class="ecliptic">Nakshatras</span>
    </label>
    <label class="indent">
      <input type="checkbox" bind:checked={showNakshatraLabels} disabled={!showNakshatras} />
      <span class="ecliptic">Labels</span>
    </label>
  </section>
  
  <section>
    <h3>Arcs</h3>
    <label>
      <input type="checkbox" bind:checked={showEquatorialArcs} />
      <span class="equatorial">Equatorial Arcs</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showEclipticArcs} />
      <span class="ecliptic">Ecliptic Arcs</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showPolarArcs} />
      <span class="polar">Polar Arcs</span>
    </label>
  </section>
  
  <section>
    <h3>Great Circles</h3>
    <label>
      <input type="checkbox" bind:checked={showPSCircle} />
      <span class="equatorial">P-S Circle</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showPPrimeCircle} />
      <span class="ecliptic">P′-S Circle</span>
    </label>
  </section>
  
  <section>
    <h3>Display</h3>
    <label>
      <input type="checkbox" bind:checked={showMarkers} />
      <span>Markers (P, P′, L, L′)</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showStar} />
      <span>Star Position (S)</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showArcLabels} />
      <span>Arc Labels</span>
    </label>
  </section>
</aside>

<style>
  .control-panel {
    position: absolute;
    top: 20px;
    left: 20px;
    background: var(--color-panel-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 16px;
    min-width: 200px;
    backdrop-filter: blur(10px);
    z-index: 10;
  }
  
  h2 {
    font-size: 20px;
    margin-bottom: 16px;
    color: #fff;
  }
  
  h3 {
    font-size: 15px;
    margin-bottom: 8px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  section {
    margin-bottom: 16px;
  }
  
  section:last-child {
    margin-bottom: 0;
  }
  
  label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    cursor: pointer;
    color: #e0e0e0;
    font-size: 15px;
  }
  
  label:hover {
    color: #fff;
  }
  
  input[type="checkbox"] {
    width: 16px;
    height: 16px;
  }
  
  .equatorial {
    color: var(--color-equatorial);
  }
  
  .ecliptic {
    color: var(--color-ecliptic);
  }
  
  .polar {
    color: var(--color-polar);
  }
  
  /* Indent for nested checkboxes */
  label.indent {
    margin-left: 24px;
    font-size: 14px;
  }
  
  label.indent input[type="checkbox"]:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  
  label.indent:has(input[type="checkbox"]:disabled) {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* Mobile toggle button */
  .mobile-toggle {
    display: none;
    position: fixed;
    top: 80px;
    left: 20px;
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
  
  .hamburger-icon {
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: 24px;
  }
  
  .hamburger-icon span {
    display: block;
    height: 2px;
    background: #fff;
    border-radius: 1px;
    transition: all 0.3s;
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
    
    .control-panel {
      position: fixed;
      top: 80px;
      left: -280px;
      max-height: calc(100vh - 100px);
      overflow-y: auto;
      transition: left 0.3s ease-in-out;
      box-shadow: 4px 0 12px rgba(0, 0, 0, 0.3);
    }
    
    .control-panel.open {
      left: 20px;
    }
  }
</style>
