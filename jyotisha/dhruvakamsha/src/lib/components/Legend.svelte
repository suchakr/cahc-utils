<script>
  let isOpen = false;
  
  function togglePanel() {
    isOpen = !isOpen;
  }
</script>

<!-- Mobile toggle button -->
<button class="mobile-toggle" on:click={togglePanel} aria-label="Toggle legend">
  <span class="legend-icon">📖</span>
</button>

<!-- Backdrop for mobile -->
{#if isOpen}
  <div class="backdrop" on:click={togglePanel}></div>
{/if}

<aside class="legend-panel" class:open={isOpen}>
  <h2>Legend</h2>
  
  <section>
    <h3>Markers</h3>
    <div class="legend-item">
      <span class="marker-icon star equatorial"></span>
      <div class="legend-text">
        <strong>P</strong> - North Celestial Pole (NCP)
      </div>
    </div>
    <div class="legend-item">
      <span class="marker-icon circle ecliptic"></span>
      <div class="legend-text">
        <strong>P′</strong> - North Ecliptic Pole (NEP)
      </div>
    </div>
    <div class="legend-item">
      <span class="marker-icon diamond equatorial"></span>
      <div class="legend-text">
        <strong>L</strong> - Vernal Equinox (0° RA, 0° Lon)
      </div>
    </div>
    <div class="legend-item">
      <span class="marker-icon diamond polar"></span>
      <div class="legend-text">
        <strong>L′</strong> - Ashvini (34° ecliptic longitude)
      </div>
    </div>
    <div class="legend-item">
      <span class="marker-icon star star-draggable"></span>
      <div class="legend-text">
        <strong>S</strong> - Star (draggable position)
      </div>
    </div>
  </section>
  
  <section>
    <h3>Coordinate Systems</h3>
    <div class="legend-item">
      <span class="color-swatch equatorial"></span>
      <span class="legend-text">Equatorial (RA/Dec)</span>
    </div>
    <div class="legend-item">
      <span class="color-swatch ecliptic"></span>
      <span class="legend-text">Ecliptic (Lon/Lat)</span>
    </div>
    <div class="legend-item">
      <span class="color-swatch polar"></span>
      <span class="legend-text">Polar (Dhruvaka/Vikṣepa)</span>
    </div>
  </section>
</aside>

<style>
  .legend-panel {
    position: absolute;
    bottom: 20px;
    left: 20px;
    background: var(--color-panel-bg);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 18px;
    min-width: 280px;
    max-width: 320px;
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
    margin-bottom: 10px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  section {
    margin-bottom: 18px;
  }
  
  section:last-child {
    margin-bottom: 0;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
    font-size: 15px;
  }
  
  .legend-item:last-child {
    margin-bottom: 0;
  }
  
  .legend-text {
    color: #e0e0e0;
    line-height: 1.4;
  }
  
  .legend-text strong {
    color: #fff;
    font-weight: 600;
  }
  
  .color-swatch {
    width: 24px;
    height: 16px;
    border-radius: 3px;
    flex-shrink: 0;
  }
  
  .marker-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  
  /* Star shape using CSS */
  .marker-icon.star::before {
    content: "★";
    font-size: 20px;
    line-height: 1;
  }
  
  /* Diamond shape using CSS */
  .marker-icon.diamond {
    width: 16px;
    height: 16px;
    transform: rotate(45deg);
    border: 2px solid;
  }
  
  /* Circle shape using CSS */
  .marker-icon.circle {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid;
    background-color: transparent;
  }
  
  .equatorial {
    color: var(--color-equatorial);
    background-color: var(--color-equatorial);
    border-color: var(--color-equatorial);
  }
  
  .ecliptic {
    color: var(--color-ecliptic);
    background-color: var(--color-ecliptic);
    border-color: var(--color-ecliptic);
  }
  
  .polar {
    color: var(--color-polar);
    background-color: var(--color-polar);
    border-color: var(--color-polar);
  }
  
  .star-draggable {
    color: var(--color-star);
  }
  
  /* Mobile toggle button */
  .mobile-toggle {
    display: none;
    position: fixed;
    bottom: 20px;
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
  
  .legend-icon {
    font-size: 24px;
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
    
    .legend-panel {
      position: fixed;
      bottom: -400px;
      left: 10px;
      right: 10px;
      padding: 12px;
      min-width: auto;
      max-width: none;
      max-height: 60vh;
      overflow-y: auto;
      font-size: 13px;
      transition: bottom 0.3s ease-in-out;
      box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .legend-panel.open {
      bottom: 80px;
    }
    
    h2 {
      font-size: 16px;
      margin-bottom: 10px;
    }
    
    h3 {
      font-size: 13px;
      margin-bottom: 6px;
    }
    
    .legend-item {
      gap: 8px;
      margin-bottom: 6px;
      font-size: 13px;
    }
    
    .color-swatch {
      width: 20px;
      height: 14px;
    }
    
    .marker-icon {
      width: 20px;
      height: 20px;
    }
    
    .marker-icon.star::before {
      font-size: 16px;
    }
    
    .marker-icon.diamond {
      width: 14px;
      height: 14px;
    }
    
    .marker-icon.circle {
      width: 16px;
      height: 16px;
    }
  }
</style>
