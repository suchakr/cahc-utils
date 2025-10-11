<script>
  export let showEquatorialGrid;
  export let showEclipticGrid;
  export let showEquator;
  export let showEcliptic;
  export let showStar;
  export let showEquatorialArcs;
  export let showEclipticArcs;
  export let showPolarArcs;
  export let showLabels;
  export let showPSCircle;
  export let showPPrimeCircle;
</script>

<aside class="control-panel">
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
      <input type="checkbox" bind:checked={showStar} />
      <span>Star Position</span>
    </label>
    <label>
      <input type="checkbox" bind:checked={showLabels} />
      <span>Labels</span>
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
</style>
