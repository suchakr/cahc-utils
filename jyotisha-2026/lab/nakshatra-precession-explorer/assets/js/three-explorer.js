      import * as THREE from 'three';
      import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

      const data = JSON.parse(document.getElementById("explorer-data").textContent);
      const stories = JSON.parse(document.getElementById("story-data").textContent);
      const container = document.getElementById("three-container");
      const threeViewToolbar = document.getElementById("three-view-toolbar");
      const threeFullscreenToggle = document.getElementById("three-fullscreen-toggle");
      const threeOrbitToggle = document.getElementById("three-orbit-toggle");
      const threeMoreToggle = document.getElementById("three-more-toggle");
      const threeMoreDrawer = document.getElementById("three-more-drawer");
      const threeToolbarPin = document.getElementById("three-toolbar-pin");
      const threeOrbitButtons = Array.from(document.querySelectorAll("[data-orbit-mode]"));
      const threeViewAnchorButtons = Array.from(document.querySelectorAll("[data-view-anchor]"));
      const threeLayerButtons = Array.from(document.querySelectorAll("[data-layer-toggle]"));
      const threeTimeButtons = Array.from(document.querySelectorAll("[data-time-action]"));
      const threeTimeSpeedButtons = Array.from(document.querySelectorAll("[data-time-speed]"));
      const threeTimeStatus = document.getElementById("three-time-status");
      const overlayLabel = document.getElementById("three-epoch-label");
      const storyStrip = document.getElementById("three-story-strip");
      const storyCaption = document.getElementById("three-story-caption");
      const storyLabelLayer = document.getElementById("three-label-layer");
      const threeDock = document.getElementById("three-dock");
      const threeDockToggle = document.getElementById("three-dock-toggle");
      const threeDockResizer = document.getElementById("three-dock-resizer");
      const threeDockTabs = Array.from(document.querySelectorAll(".three-dock-tab"));
      const threeDockPanels = {
        static: document.getElementById("three-dock-static"),
        stories: document.getElementById("three-dock-stories"),
      };
      const threeStorySearch = document.getElementById("three-story-search");
      const threeStorySelect = document.getElementById("three-story-select");
      const threeStoryEditor = document.getElementById("three-story-editor");
      const threeStoryStatus = document.getElementById("three-story-status");
      const threeStoryRun = document.getElementById("three-story-run");
      const threeStoryStop = document.getElementById("three-story-stop");
      const threeStoryReset = document.getElementById("three-story-reset");
      const threeStoryCopy = document.getElementById("three-story-copy");
      const threeVysuEditor = document.getElementById("three-vysu-editor");
      const threeVysuLines = document.getElementById("three-vysu-lines");
      const threeVysuFontSize = document.getElementById("three-vysu-font-size");
      const threeVysuRun = document.getElementById("three-vysu-run");
      const threeVysuStatus = document.getElementById("three-vysu-status");
      const threeCameraDirective = document.getElementById("three-camera-directive");
      const threeCameraGrab = document.getElementById("three-camera-grab");
      const threeLightPreset = document.getElementById("three-light-preset");
      const threeDebugJson = document.getElementById("three-debug-json");
      const threeDebugStatus = document.getElementById("three-debug-status");
      const threeDebugCapture = document.getElementById("three-debug-capture");
      const threeDebugApply = document.getElementById("three-debug-apply");
      const threeDebugCopy = document.getElementById("three-debug-copy");
      const threeDebugReset = document.getElementById("three-debug-reset");
      const threeDebugToggles = document.getElementById("three-debug-toggles");


      const R = 100;
      const BAND_HALF = data.meta.ecliptic_band_half_width_deg;
      let scene, camera, renderer, controls;
      let siderealGroup, seasonalGroup;
      let equatorLine, equinoxMarkers, poleDot, southPoleDot, southPoleLabel, nsAxisLine, eclipticPlane, equatorialPlane;
      let eclipticCircle;
      let starPoints;
      const starGroupRefs = [];
      let poleTrackCircle, poleTrackArc, poleTrackLabel;
      let movingPoleLabel = null;
      const eclipticPoleDots = [];
      const eclipticPoleLabels = [];
      const eclipticPoleRefs = [];
      const gridRefs = { parallels: [], meridians: [], equatorialParallels: [], equatorialMeridians: [] };
      const bandRefs = { meshes: [], dividers: [], labels: [] };
      const nakshatraLineRefs = [];
      const nakshatraLabelRefs = [];
      const polarItemRefs = [];
      const seasonalMarkerRefs = [];
      const activeStoryTimers = [];
      let activeStoryId = null;
      let activeStoryFrame = null;
      let storyLabels = {};
      let builtEclipticGridStep = null;
      let builtEquatorialGridStep = null;
      const activeTransitionTargets = new Set();
      const activeTransitionObjects = new Set();
      const targetVisibilityOverrides = new Map();
      const focusedPolarTargets = { north: new Set(), south: new Set() };
      const focusedSeasonalTargets = new Set();
      let orbitMode = "free";
      const timeFlow = { direction: 0, speed: 1, loop: true, timer: null };
      const threeDebugUiFields = [
        ["showGrid", "Ecliptic grid"],
        ["showEquatorialGrid", "Equatorial grid"],
        ["showReferencePlanes", "Reference planes"],
        ["showNsAxis", "NS axis"],
        ["showEclipticBand", "Ecliptic band"],
        ["showEclipticDividers", "Sector dividers"],
        ["showEclipticLabels", "Sector labels"],
        ["showEclipticPoles", "Ecliptic poles"],
        ["showStars", "Stars"],
        ["showNakshatraStars", "Nakshatra stars"],
        ["showNakshatraLines", "Nakshatra lines"],
        ["showNakshatraLabels", "Nakshatra labels"],
        ["showPolarItems", "Polar items"],
        ["showNorthPolarItems", "North polar items"],
        ["showSouthPolarItems", "South polar items"],
        ["showPoleTrack", "Precession circle"],
        ["showSeasonalFrame", "Seasonal frame"],
        ["showOverlay", "Overlay caption"],
      ];
      const defaultThreeSettings = {
        lightPreset: "night",
        epochYear: -1800,
        camera: {
          position: { x: -147.464, y: 73.504, z: 234.757 },
          target: { x: 0, y: 0, z: 0 },
          fov: 45,
          minDistance: 130,
          maxDistance: 600,
        },
        grid: {
          eclipticStepDeg: 30,
          equatorialStepDeg: 30,
          parallelColor: "#667788",
          parallelOpacity: 0.4,
          meridianColor: "#556677",
          meridianOpacity: 0.4,
          equatorialColor: "#884444",
          equatorialOpacity: 0.28,
        },
        ecliptic: {
          bandOpacity: 0.18,
          dividerOpacity: 0.32,
          circleColor: "#d4a56a",
          circleOpacity: 0.65,
          sectorLabelSize: 5.0,
          sectorLabelOpacity: 0.72,
          poleLabelSize: 5.0,
          poleLabelOpacity: 0.3,
        },
        reference: {
          eclipticPlaneColor: "#d4a56a",
          eclipticPlaneOpacity: 0.045,
          equatorialPlaneColor: "#cc3333",
          equatorialPlaneOpacity: 0.04,
          nsAxisColor: "#a7b4c7",
          nsAxisOpacity: 0.32,
        },
        stars: {
          size: 2.8,
          opacity: 0.88,
        },
        nakshatras: {
          color: "#8eaccb",
          opacity: 0.88,
          selectedColor: "#d6b27a",
          selectedOpacity: 1.0,
          labelOpacity: 0.5,
          labelSize: 5.0,
        },
        polarItems: {
          color: "#6f86a1",
          opacity: 0.55,
          labelOpacity: 0.65,
          starOpacity: 0.72,
          labelSize: 5.0,
        },
        poleTrack: {
          color: "#6a7b91",
          opacity: 0.4,
          arcColor: "#8899bb",
          arcOpacity: 0.05,
          dotColor: "#944566",
          trackLabelSize: 4.5,
          trackLabelOpacity: 0.4,
          movingPoleLabelSize: 5.0,
          movingPoleLabelOpacity: 0.7,
        },
        seasonal: {
          equatorColor: "#cc3333",
          equatorOpacity: 0.78,
          markerScale: 1.0,
          markerLabelSize: 7.5,
          markerLabelOpacity: 0.8,
        },
        overlay: {
          fontSizeRem: 1.8,
          opacity: 1.0,
        },
        targetStyles: {},
        ui: {
          showGrid: true,
          showEquatorialGrid: false,
          showReferencePlanes: false,
          showEclipticPlane: true,
          showEquatorialPlane: true,
          showNsAxis: false,
          showEclipticBand: true,
          showEclipticDividers: true,
          showEclipticLabels: true,
          showEclipticPoles: true,
          showStars: true,
          showNakshatraStars: true,
          showNakshatraLines: true,
          showNakshatraLabels: true,
          showPolarItems: true,
          showNorthPolarItems: true,
          showSouthPolarItems: true,
          showNEP: true,
          showSEP: true,
          showNP: true,
          showSP: true,
          showPoleTrack: true,
          showSeasonalFrame: true,
          showOverlay: true,
        },
      };
      let threeSettings = JSON.parse(JSON.stringify(defaultThreeSettings));
      const runtimePreciseStyleRegistry = new Set();

      /* ── helpers ─────────────────────────────────────────── */
      function toCart(lonDeg, latDeg, r) {
        const lon = lonDeg * Math.PI / 180;
        const lat = latDeg * Math.PI / 180;
        return new THREE.Vector3(
          r * Math.cos(lat) * Math.cos(lon),
          r * Math.sin(lat),
          r * Math.cos(lat) * Math.sin(lon)
        );
      }

      function circlePoints(latDeg, r, n) {
        const pts = [];
        for (let i = 0; i <= n; i++) pts.push(toCart(i * 360 / n, latDeg, r));
        return pts;
      }

      function meridianPoints(lonDeg, r, n) {
        const pts = [];
        for (let i = 0; i <= n; i++) pts.push(toCart(lonDeg, -90 + i * 180 / n, r));
        return pts;
      }

      function gridStep(value) {
        const numeric = Number(value);
        if (!Number.isFinite(numeric)) return 30;
        return Math.min(90, Math.max(5, numeric));
      }

      function removeObjects(refs, group) {
        refs.splice(0).forEach((object) => {
          group.remove(object);
          object.geometry?.dispose?.();
          if (object.material) object.material.dispose?.();
        });
      }

      function makeTextSprite(text, opts) {
        const fontSize = opts.fontSize || 48;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.font = `${opts.bold ? 'bold ' : ''}${fontSize}px sans-serif`;
        const metrics = ctx.measureText(text);
        const w = Math.ceil(metrics.width) + 12;
        const h = fontSize + 12;
        canvas.width = w;
        canvas.height = h;
        ctx.font = `${opts.bold ? 'bold ' : ''}${fontSize}px sans-serif`;
        ctx.fillStyle = opts.color || '#ffffff';
        ctx.textBaseline = 'middle';
        ctx.textAlign = 'center';
        ctx.fillText(text, w / 2, h / 2);
        const tex = new THREE.CanvasTexture(canvas);
        tex.minFilter = THREE.LinearFilter;
        const mat = new THREE.SpriteMaterial({
          map: tex, transparent: true, opacity: opts.opacity || 0.85,
          depthWrite: false, depthTest: false
        });
        const sprite = new THREE.Sprite(mat);
        // Change: Use absolute world units for height, then scale width proportionally
        const hUnits = opts.size || 8.0; 
        sprite.scale.set(hUnits * w / h, hUnits, 1);
        sprite.userData.aspect = w / h;
        sprite.userData.text = text;
        sprite.userData.textStyle = {
          color: opts.color || '#ffffff',
          fontSize,
          bold: Boolean(opts.bold),
        };
        return sprite;
      }

      function setSpriteHeight(sprite, height) {
        const aspect = sprite?.userData?.aspect || 1;
        sprite.scale.set(height * aspect, height, 1);
      }

      function setSpriteTextColor(sprite, color) {
        if (!sprite || !color || sprite.userData?.textStyle?.color === color) return;
        const text = sprite.userData?.text || "";
        const textStyle = { ...(sprite.userData?.textStyle || {}), color };
        const fontSize = textStyle.fontSize || 48;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.font = `${textStyle.bold ? 'bold ' : ''}${fontSize}px sans-serif`;
        const metrics = ctx.measureText(text);
        const w = Math.ceil(metrics.width) + 12;
        const h = fontSize + 12;
        canvas.width = w;
        canvas.height = h;
        ctx.font = `${textStyle.bold ? 'bold ' : ''}${fontSize}px sans-serif`;
        ctx.fillStyle = color;
        ctx.textBaseline = 'middle';
        ctx.textAlign = 'center';
        ctx.fillText(text, w / 2, h / 2);
        const tex = new THREE.CanvasTexture(canvas);
        tex.minFilter = THREE.LinearFilter;
        const oldMap = sprite.material?.map;
        sprite.material.map = tex;
        sprite.material.needsUpdate = true;
        oldMap?.dispose?.();
        sprite.userData.aspect = w / h;
        sprite.userData.textStyle = textStyle;
      }

      function sectorHSL(index) {
        const h = (index * 360 / 27 + 15) % 360;
        return `hsl(${h}, 38%, 52%)`;
      }

      function sectorHex(index) {
        const h = (index * 360 / 27 + 15) % 360;
        const c = new THREE.Color();
        c.setHSL(h / 360, 0.38, 0.52);
        return c;
      }

      function setDebugStatus(text) {
        if (threeDebugStatus) threeDebugStatus.textContent = text;
      }

      function setStoryStatus(text) {
        if (threeStoryStatus) threeStoryStatus.textContent = text;
      }

      function setVysuStatus(text) {
        if (threeVysuStatus) threeVysuStatus.textContent = text;
      }

      function syncVysuLineNumbers() {
        if (!threeVysuEditor || !threeVysuLines) return;
        const count = Math.max(1, threeVysuEditor.value.split(/\r?\n/).length);
        let text = "";
        for (let i = 1; i <= count; i += 1) text += `${i}\n`;
        threeVysuLines.textContent = text;
        threeVysuLines.scrollTop = threeVysuEditor.scrollTop;
      }

      function setVysuEditorFontSize(sizePx) {
        if (!threeVysuEditor) return;
        const size = Math.min(24, Math.max(11, Number(sizePx) || 13));
        const lineHeight = Math.round(size * 1.42 * 100) / 100;
        const shell = threeVysuEditor.closest(".vysu-editor-shell");
        if (shell) {
          shell.style.setProperty("--vysu-editor-font-size", `${size}px`);
          shell.style.setProperty("--vysu-editor-line-height", `${lineHeight}px`);
        }
        if (threeVysuFontSize) threeVysuFontSize.value = String(size);
        try { window.localStorage.setItem("vysuEditorFontSize", String(size)); } catch (error) {}
        syncVysuLineNumbers();
      }

      function initVysuEditorChrome() {
        if (!threeVysuEditor) return;
        let savedSize = 13;
        try { savedSize = Number(window.localStorage.getItem("vysuEditorFontSize")) || 13; } catch (error) {}
        setVysuEditorFontSize(savedSize);
        threeVysuEditor.addEventListener("input", syncVysuLineNumbers);
        threeVysuEditor.addEventListener("scroll", syncVysuLineNumbers);
        if (threeVysuFontSize) {
          threeVysuFontSize.addEventListener("change", () => setVysuEditorFontSize(threeVysuFontSize.value));
          threeVysuFontSize.addEventListener("input", () => setVysuEditorFontSize(threeVysuFontSize.value));
        }
        syncVysuLineNumbers();
      }

      function setDockWidth(widthPx) {
        if (!threeDock) return;
        const workspace = threeDock.closest(".three-workspace");
        if (!workspace || workspace.classList.contains("dock-collapsed")) return;
        const workspaceWidth = workspace.getBoundingClientRect().width || window.innerWidth;
        const max = Math.max(360, Math.min(760, workspaceWidth - 520));
        const width = Math.min(max, Math.max(360, Math.round(Number(widthPx) || 440)));
        workspace.style.gridTemplateColumns = `minmax(28rem, 1fr) ${width}px`;
        try { window.localStorage.setItem("threeDockWidth", String(width)); } catch (error) {}
        window.dispatchEvent(new Event("resize"));
      }

      function initDockResizer() {
        if (!threeDock || !threeDockResizer) return;
        let savedWidth = null;
        try { savedWidth = Number(window.localStorage.getItem("threeDockWidth")) || null; } catch (error) {}
        if (savedWidth) setDockWidth(savedWidth);
        threeDockResizer.addEventListener("pointerdown", (event) => {
          if (window.matchMedia("(max-width: 900px)").matches) return;
          event.preventDefault();
          threeDockResizer.setPointerCapture(event.pointerId);
          const onMove = (moveEvent) => {
            const workspace = threeDock.closest(".three-workspace");
            if (!workspace) return;
            const rect = workspace.getBoundingClientRect();
            setDockWidth(rect.right - moveEvent.clientX);
          };
          const onUp = (upEvent) => {
            threeDockResizer.releasePointerCapture(upEvent.pointerId);
            window.removeEventListener("pointermove", onMove);
            window.removeEventListener("pointerup", onUp);
          };
          window.addEventListener("pointermove", onMove);
          window.addEventListener("pointerup", onUp);
        });
      }

      function formatCameraNumber(value) {
        return Number(value || 0).toFixed(3).replace(/\.?0+$/, "");
      }

      function currentCameraDirective() {
        if (!camera || !controls) return "camera pos 0,0,0 target 0,0,0 fov 45 over 900";
        const pos = [camera.position.x, camera.position.y, camera.position.z].map(formatCameraNumber).join(",");
        const target = [controls.target.x, controls.target.y, controls.target.z].map(formatCameraNumber).join(",");
        const fov = formatCameraNumber(camera.fov || 45);
        return `camera pos ${pos} target ${target} fov ${fov} over 900`;
      }

      async function grabCameraDirective() {
        const directive = currentCameraDirective();
        if (threeCameraDirective) threeCameraDirective.value = directive;
        try {
          if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
          await navigator.clipboard.writeText(directive);
          setVysuStatus("Copied camera directive.");
        } catch (error) {
          setVysuStatus("Camera directive ready.");
        }
      }

      function cloneSettings(settings) {
        return JSON.parse(JSON.stringify(settings));
      }

      function fullscreenIcon(expanded) {
        return expanded
          ? '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3v3a2 2 0 0 1-2 2H3"></path><path d="M16 3v3a2 2 0 0 0 2 2h3"></path><path d="M8 21v-3a2 2 0 0 0-2-2H3"></path><path d="M16 21v-3a2 2 0 0 1 2-2h3"></path></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M16 3h3a2 2 0 0 1 2 2v3"></path><path d="M8 21H5a2 2 0 0 1-2-2v-3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path></svg>';
      }

      function syncFullscreenButton(expanded) {
        if (!threeFullscreenToggle) return;
        threeFullscreenToggle.innerHTML = fullscreenIcon(expanded);
        threeFullscreenToggle.title = expanded ? "Exit fullscreen" : "Fullscreen";
        threeFullscreenToggle.setAttribute("aria-label", expanded ? "Exit fullscreen" : "Fullscreen");
      }

      function applyOrbitMode(mode = orbitMode) {
        orbitMode = mode;
        threeOrbitButtons.forEach((button) => {
          const active = button.dataset.orbitMode === orbitMode;
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        if (threeOrbitToggle) {
          const locked = orbitMode === "lock";
          threeOrbitToggle.textContent = locked ? "Lock" : "Free";
          threeOrbitToggle.classList.toggle("active", !locked);
          threeOrbitToggle.setAttribute("aria-pressed", locked ? "true" : "false");
          threeOrbitToggle.title = locked ? "Click to allow free orbit" : "Click to lock rotation";
          threeOrbitToggle.setAttribute("aria-label", locked ? "Click to allow free orbit" : "Click to lock rotation");
        }
        if (!controls) return;
        controls.enableRotate = orbitMode !== "lock";
        controls.minAzimuthAngle = -Infinity;
        controls.maxAzimuthAngle = Infinity;
        if (orbitMode === "xy") {
          const polar = THREE.MathUtils.clamp(controls.getPolarAngle(), 0.001, Math.PI - 0.001);
          controls.minPolarAngle = polar;
          controls.maxPolarAngle = polar;
        } else {
          controls.minPolarAngle = 0;
          controls.maxPolarAngle = Math.PI;
        }
        controls.update();
      }

      function setMoreDrawer(open) {
        if (!threeMoreDrawer || !threeMoreToggle) return;
        threeMoreDrawer.classList.toggle("open", open);
        threeMoreToggle.classList.toggle("active", open);
        threeMoreToggle.textContent = open ? "Less" : "More";
        threeMoreToggle.title = open ? "Hide more controls" : "Show more controls";
        threeMoreToggle.setAttribute("aria-label", open ? "Hide more controls" : "Show more controls");
        threeMoreToggle.setAttribute("aria-expanded", open ? "true" : "false");
      }

      function closeMoreDrawer(force = false) {
        if (!force && threeViewToolbar?.classList.contains("pinned")) return;
        setMoreDrawer(false);
      }

      function toggleMoreDrawer() {
        setMoreDrawer(!threeMoreDrawer?.classList.contains("open"));
      }

      function layerFlagGroups() {
        return {
          stars: ["showStars"],
          nakshatras: ["showNakshatraStars", "showNakshatraLines"],
          labels: ["showNakshatraLabels", "showEclipticLabels"],
          grid: ["showGrid", "showEquatorialGrid"],
          sectors: ["showEclipticBand", "showEclipticDividers", "showEclipticLabels"],
          seasonal: ["showSeasonalFrame"],
          poles: ["showEclipticPoles", "showPolarItems", "showPoleTrack", "showNP", "showSP"],
        };
      }

      function syncLayerButtons() {
        const groups = layerFlagGroups();
        threeLayerButtons.forEach((button) => {
          const flags = groups[button.dataset.layerToggle] || [];
          const active = flags.length > 0 && flags.every((flag) => threeSettings.ui[flag] !== false);
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
      }

      function setLayerGroup(name) {
        const flags = layerFlagGroups()[name] || [];
        if (!flags.length) return;
        const active = flags.every((flag) => threeSettings.ui[flag] !== false);
        flags.forEach((flag) => {
          threeSettings.ui[flag] = !active;
        });
        applyThreeSettings({ preserveEpoch: true, preserveCamera: true });
        syncThreeDebugTogglesFromSettings();
        syncDebugTextareaFromLive();
        syncLayerButtons();
      }

      function cameraAnchor(anchor) {
        const target = { x: 0, y: 0, z: 0 };
        const home = cloneSettings(defaultThreeSettings).camera;
        if (anchor === "home") return home;
        if (anchor === "top") return { position: { x: 0, y: 325, z: 0.1 }, target, fov: 42 };
        if (anchor === "side") return { position: { x: 325, y: 0, z: 0 }, target, fov: 42 };
        if (anchor === "pole") {
          const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
          const pole = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, 325);
          return { position: { x: pole.x, y: pole.y, z: pole.z }, target, fov: 42 };
        }
        if (anchor === "equator") {
          const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
          const point = toCart(epoch.vernal_equinox_lon_deg + 90, 0, 325);
          return { position: { x: point.x, y: point.y, z: point.z }, target, fov: 42 };
        }
        return home;
      }

      function flyToCamera(cueCamera, duration = 700) {
        if (!camera || !controls || !cueCamera) return;
        const startTime = performance.now();
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const endPos = new THREE.Vector3(
          cueCamera.position?.x ?? camera.position.x,
          cueCamera.position?.y ?? camera.position.y,
          cueCamera.position?.z ?? camera.position.z
        );
        const endTarget = new THREE.Vector3(
          cueCamera.target?.x ?? controls.target.x,
          cueCamera.target?.y ?? controls.target.y,
          cueCamera.target?.z ?? controls.target.z
        );
        const startFov = camera.fov;
        const endFov = cueCamera.fov ?? camera.fov;
        const restoreOrbitMode = orbitMode;
        controls.minPolarAngle = 0;
        controls.maxPolarAngle = Math.PI;
        const tick = (now) => {
          const t = Math.min(1, (now - startTime) / duration);
          const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
          camera.position.lerpVectors(startPos, endPos, eased);
          controls.target.lerpVectors(startTarget, endTarget, eased);
          camera.fov = startFov + (endFov - startFov) * eased;
          camera.updateProjectionMatrix();
          controls.update();
          if (t < 1) {
            window.requestAnimationFrame(tick);
          } else {
            threeSettings.camera.position = {
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            };
            threeSettings.camera.target = {
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            };
            threeSettings.camera.fov = Number(camera.fov.toFixed(3));
            applyOrbitMode(restoreOrbitMode);
            syncDebugTextareaFromLive();
          }
        };
        window.requestAnimationFrame(tick);
      }

      function syncTimeControls() {
        threeTimeSpeedButtons.forEach((button) => {
          const active = Number(button.dataset.timeSpeed) === timeFlow.speed;
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        threeTimeButtons.forEach((button) => {
          const action = button.dataset.timeAction;
          const active = action === "loop" ? timeFlow.loop : (action === "play" && timeFlow.direction > 0) || (action === "reverse" && timeFlow.direction < 0) || (action === "pause" && timeFlow.direction === 0);
          button.classList.toggle("active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        const epoch = data.epochs[window.explorerState?.epochIndex ?? 0] || data.epochs[0];
        const direction = timeFlow.direction > 0 ? "forward" : timeFlow.direction < 0 ? "backward" : "paused";
        if (threeTimeStatus && epoch) {
          threeTimeStatus.textContent = `${epoch.label} · ${timeFlow.speed}x ${direction}`;
        }
      }

      function stopToolbarTime() {
        if (timeFlow.timer !== null) {
          window.clearInterval(timeFlow.timer);
          timeFlow.timer = null;
        }
        timeFlow.direction = 0;
        syncTimeControls();
      }

      function stepToolbarTime(delta) {
        const st = window.explorerState;
        if (!st || typeof window.explorerRender !== "function") return;
        let next = st.epochIndex + delta;
        if (next < 0 || next >= data.epochs.length) {
          if (!timeFlow.loop) {
            stopToolbarTime();
            return;
          }
          next = next < 0 ? data.epochs.length - 1 : 0;
        }
        st.epochIndex = next;
        window.explorerRender();
        syncTimeControls();
      }

      function startToolbarTime(direction) {
        if (timeFlow.timer !== null) {
          window.clearInterval(timeFlow.timer);
          timeFlow.timer = null;
        }
        timeFlow.direction = direction;
        const interval = Math.max(60, 480 / timeFlow.speed);
        timeFlow.timer = window.setInterval(() => stepToolbarTime(timeFlow.direction), interval);
        syncTimeControls();
      }


      const defaultVyomaSutra = `# Visualize axial precession against the fixed nakshatra sky
stage blank night year -1800
camera pos -147.464,73.504,234.757 target 0,0,0

caption "Visualize Precession" 1200:250:350
show eclipticGrid ; wait 200 ; show eclipticNakSegments
wait 200 ; fade stars
wait 100 ; rollout naks
wait 200 ; show seasonalFrame
wait 100 ; show poleTrack
wait 100 ; show overlay

wait 300 ; caption "1800 BCE" 1000:200:300
wait 200 ; travel -1800 to -800 5000: step 100`;

      const vysuTargetAliases = {
        eclipticgrid: "eclipticGrid",
        eclgrid: "eclipticGrid",
        eclgridwire: "eclipticGrid",
        eclipticnaksegments: "eclipticNakSegments",
        eclipticnakssegments: "eclipticNakSegments",
        naksegments: "eclipticNakSegments",
        nakssegments: "eclipticNakSegments",
        eclipticsegments: "eclipticNakSegments",
        eclipticband: "eclipticBand",
        eclipticdividers: "eclipticDividers",
        sectordividers: "eclipticDividers",
        eclipticlabels: "eclipticLabels",
        sectorlabels: "eclipticLabels",
        eclipticpoles: "eclipticPoles",
        eclipticplane: "eclipticPlane",
        equatorialplane: "equatorialPlane",
        equatorialgrid: "equatorialGrid",
        equatorgrid: "equatorialGrid",
        eqgrid: "equatorialGrid",
        eq: "equatorialGrid",
        referenceplanes: "referencePlanes",
        refs: "referencePlanes",
        nsaxis: "nsAxis",
        axis: "nsAxis",
        nep: "NEP",
        sep: "SEP",
        np: "NP",
        sp: "SP",
        stars: "stars",
        naks: "nakshatras",
        nak: "nakshatras",
        nakshatra: "nakshatras",
        nakshatras: "nakshatras",
        seasonalframe: "seasonalFrame",
        seasons: "seasonalFrame",
        rtus: "seasonalFrame",
        rtu: "seasonalFrame",
        poletrack: "poleTrack",
        polepath: "poleTrack",
        precessioncircle: "poleTrack",
        overlay: "overlay",
        polaritems: "polarItems",
        northpolaritems: "northPolarItems",
        northpolar: "northPolarItems",
        southpolaritems: "southPolarItems",
        southpolar: "southPolarItems",
        precessioncircle: "precessionCircle",
        precession: "precessionCircle",
        equator: "equator",
        ve: "VE",
        ss: "SS",
        ae: "AE",
        ws: "WS",
        agastya: "agastya",
        canopus: "agastya",
        thuban: "thuban",
        abhayadhruva: "thuban",
        polaris: "polaris",
        matsyadhruva: "polaris",
        matsya: "matsya",
        sisumara: "sisumara",
        shishumara: "sisumara",
        shimshumara: "sisumara",
        fullscreen: "fullscreen",
      };

      function stripVysuComment(line) {
        let quote = false;
        for (let i = 0; i < line.length; i += 1) {
          const ch = line[i];
          if (ch === '"') quote = !quote;
          if (!quote && ch === "#") {
            const hex = line.slice(i + 1).match(/^([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(\b|\s|$)/);
            if (hex) {
              i += hex[1].length;
              continue;
            }
            return line.slice(0, i);
          }
        }
        return line;
      }

      function splitVysuStatements(line) {
        const statements = [];
        let quote = false;
        let start = 0;
        for (let i = 0; i < line.length; i += 1) {
          const ch = line[i];
          if (ch === '"') quote = !quote;
          if (!quote && ch === ";") {
            const part = line.slice(start, i).trim();
            if (part) statements.push(part);
            start = i + 1;
          }
        }
        const tail = line.slice(start).trim();
        if (tail) statements.push(tail);
        return statements;
      }

      function tokenizeVysuStatement(statement) {
        const tokens = [];
        const pattern = /"[^"]*"|\S+/g;
        let match;
        while ((match = pattern.exec(statement)) !== null) tokens.push(match[0]);
        return tokens;
      }

      function parseVysuDuration(token) {
        if (!token) return null;
        const match = String(token).match(/^(\d+):(\d*)?(?::(\d*)?)?$/);
        if (!match) return null;
        const out = { duration: Number(match[1]) };
        if (match[2] !== undefined && match[2] !== "") out.fadeIn = Number(match[2]);
        if (match[3] !== undefined && match[3] !== "") out.fadeOut = Number(match[3]);
        return out;
      }

      function parseVysuVec3(token) {
        const parts = String(token || "").split(",").map(Number);
        if (parts.length !== 3 || parts.some((part) => !Number.isFinite(part))) return null;
        return { x: parts[0], y: parts[1], z: parts[2] };
      }

      function parseVysuAlpha(token) {
        const raw = String(token || "").trim();
        let value = null;
        if (/^%\d+(?:\.\d+)?$/.test(raw)) value = Number(raw.slice(1)) / 100;
        else if (/^\d+(?:\.\d+)?%$/.test(raw)) value = Number(raw.slice(0, -1)) / 100;
        else if (/^(?:0?\.\d+|1(?:\.0+)?)$/.test(raw)) value = Number(raw);
        else if (/^\d+(?:\.\d+)?$/.test(raw)) {
          const number = Number(raw);
          if (number <= 1) value = number;
        }
        return Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : null;
      }

      function parseVysuColor(token) {
        const raw = String(token || "").trim();
        if (/^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$/.test(raw)) return raw;
        const named = new Set(["white", "black", "red", "orange", "yellow", "green", "blue", "cyan", "teal", "purple", "magenta", "pink", "gray", "grey", "gold", "brown"]);
        if (named.has(raw.toLowerCase())) return raw.toLowerCase();
        return null;
      }

      function normalizeVysuTarget(token, warnings, lineNumber) {
        const raw = String(token || "").trim();
        if (!raw) return null;
        if (/^[$*@]/.test(raw)) return raw;
        const key = raw.replace(/[._-]/g, "").toLowerCase();
        const target = vysuTargetAliases[key] || raw;
        const supported = new Set([
          "eclipticGrid", "equatorialGrid", "referencePlanes", "eclipticPlane", "equatorialPlane", "nsAxis",
          "eclipticNakSegments", "eclipticBand", "eclipticDividers", "eclipticLabels", "eclipticPoles",
          "stars", "nakshatras", "seasonalFrame", "poleTrack", "precessionCircle",
          "overlay", "polarItems", "northPolarItems", "southPolarItems", "NEP", "SEP", "NP", "SP",
          "equator", "VE", "SS", "AE", "WS", "agastya", "thuban", "polaris", "matsya", "sisumara"
        ]);
        if (!supported.has(target)) {
          warnings.push(`Line ${lineNumber}: unsupported target "${raw}".`);
          return null;
        }
        return target;
      }

      function stylePatchForTarget(target, style) {
        const patch = {};
        const put = (path, value) => {
          let cursor = patch;
          path.slice(0, -1).forEach((key) => {
            if (!cursor[key]) cursor[key] = {};
            cursor = cursor[key];
          });
          cursor[path[path.length - 1]] = value;
        };
        const color = style.color || style.lineColor;
        const alpha = style.alpha ?? style.opacity;
        const fontSize = style.fontSize;
        const pointSize = style.pointSize ?? style.starSize;

        if (target === "eclipticGrid") {
          if (color) {
            put(["grid", "parallelColor"], color);
            put(["grid", "meridianColor"], color);
          }
          if (alpha !== undefined) {
            put(["grid", "parallelOpacity"], alpha);
            put(["grid", "meridianOpacity"], alpha);
          }
        } else if (target === "equatorialGrid") {
          if (color) put(["grid", "equatorialColor"], color);
          if (alpha !== undefined) put(["grid", "equatorialOpacity"], alpha);
        } else if (target === "nsAxis") {
          if (color) put(["reference", "nsAxisColor"], color);
          if (alpha !== undefined) put(["reference", "nsAxisOpacity"], alpha);
        } else if (target === "eclipticPlane") {
          if (color) put(["reference", "eclipticPlaneColor"], color);
          if (alpha !== undefined) put(["reference", "eclipticPlaneOpacity"], alpha);
        } else if (target === "equatorialPlane") {
          if (color) put(["reference", "equatorialPlaneColor"], color);
          if (alpha !== undefined) put(["reference", "equatorialPlaneOpacity"], alpha);
        } else if (target === "stars") {
          if (alpha !== undefined) put(["stars", "opacity"], alpha);
          if (pointSize !== undefined) put(["stars", "size"], pointSize);
        } else if (target === "nakshatras") {
          if (color) put(["nakshatras", "color"], color);
          if (alpha !== undefined) put(["nakshatras", "opacity"], alpha);
          if (fontSize !== undefined) put(["nakshatras", "labelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["nakshatras", "labelOpacity"], style.labelAlpha);
        } else if (target === "polarItems" || target === "northPolarItems" || target === "southPolarItems") {
          if (color) put(["polarItems", "color"], color);
          if (alpha !== undefined) put(["polarItems", "opacity"], alpha);
          if (fontSize !== undefined) put(["polarItems", "labelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["polarItems", "labelOpacity"], style.labelAlpha);
        } else if (target === "poleTrack" || target === "precessionCircle") {
          if (color) put(["poleTrack", "color"], color);
          if (alpha !== undefined) put(["poleTrack", "opacity"], alpha);
          if (fontSize !== undefined) put(["poleTrack", "trackLabelSize"], fontSize);
        } else if (target === "seasonalFrame") {
          if (color) put(["seasonal", "equatorColor"], color);
          if (alpha !== undefined) put(["seasonal", "equatorOpacity"], alpha);
          if (fontSize !== undefined) put(["seasonal", "markerLabelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["seasonal", "markerLabelOpacity"], style.labelAlpha);
        } else if (target === "eclipticNakSegments" || target === "eclipticBand" || target === "eclipticLabels") {
          if (color) put(["ecliptic", "circleColor"], color);
          if (alpha !== undefined) put(["ecliptic", "circleOpacity"], alpha);
          if (fontSize !== undefined) put(["ecliptic", "sectorLabelSize"], fontSize);
          if (style.labelAlpha !== undefined) put(["ecliptic", "sectorLabelOpacity"], style.labelAlpha);
        } else if (target === "overlay") {
          if (alpha !== undefined) put(["overlay", "opacity"], alpha);
          if (fontSize !== undefined) put(["overlay", "fontSizeRem"], fontSize);
        }
        return Object.keys(patch).length ? patch : null;
      }

      function gridPatchForVySu(args, warnings, lineNumber) {
        const kind = String(args[0] || "").toLowerCase();
        const step = Number(args[1]);
        const color = parseVysuColor(args[2]);
        const patch = { grid: {}, ui: {} };
        if (!Number.isFinite(step)) {
          warnings.push(`Line ${lineNumber}: grid needs a numeric step, e.g. grid ecliptic 15 blue.`);
          return null;
        }
        if (kind === "ecliptic" || kind === "ecl") {
          patch.grid.eclipticStepDeg = step;
          if (color) {
            patch.grid.parallelColor = color;
            patch.grid.meridianColor = color;
          }
          patch.ui.showGrid = true;
        } else if (kind === "equatorial" || kind === "equator" || kind === "eq") {
          patch.grid.equatorialStepDeg = step;
          if (color) patch.grid.equatorialColor = color;
          patch.ui.showEquatorialGrid = true;
        } else {
          warnings.push(`Line ${lineNumber}: grid kind must be ecliptic or equatorial.`);
          return null;
        }
        return patch;
      }

      function compileVyomaSutra(source) {
        const warnings = [];
        const cues = [];
        const initial = { ui: {} };
        let pendingWait = 0;
        let emitted = 0;
        const blankUi = {
          showGrid: false,
          showEquatorialGrid: false,
          showReferencePlanes: false,
          showEclipticPlane: false,
          showEquatorialPlane: false,
          showNsAxis: false,
          showEclipticBand: false,
          showEclipticDividers: false,
          showEclipticLabels: false,
          showEclipticPoles: false,
          showStars: false,
          showNakshatraStars: false,
          showNakshatraLines: false,
          showNakshatraLabels: false,
          showPolarItems: false,
          showNorthPolarItems: false,
          showSouthPolarItems: false,
          showNEP: false,
          showSEP: false,
          showNP: false,
          showSP: false,
          showPoleTrack: false,
          showSeasonalFrame: false,
          showOverlay: false,
        };

        const cueTime = () => {
          if (emitted === 0 && pendingWait === 0) return 0;
          const wait = pendingWait;
          pendingWait = 0;
          return `+${wait}`;
        };
        const addCue = (cue) => {
          cues.push({ at: cueTime(), ...cue });
          emitted += 1;
        };

        source.split(/\n/).forEach((line, lineIndex) => {
          const lineNumber = lineIndex + 1;
          splitVysuStatements(stripVysuComment(line)).forEach((statement) => {
            const tokens = tokenizeVysuStatement(statement);
            if (tokens.length === 0) return;
            const directive = tokens[0].toLowerCase();
            const args = tokens.slice(1);

            if (directive === "stage") {
              for (let i = 0; i < args.length; i += 1) {
                const arg = args[i].toLowerCase();
                if (arg === "blank") Object.assign(initial.ui, blankUi);
                else if (arg === "night" || arg === "twilight" || arg === "day") initial.lightPreset = arg;
                else if (arg === "year" || arg === "epoch") {
                  const year = Number(args[i + 1]);
                  if (Number.isFinite(year)) {
                    initial.epochYear = year;
                    i += 1;
                  } else warnings.push(`Line ${lineNumber}: stage ${arg} needs a numeric value.`);
                }
                else warnings.push(`Line ${lineNumber}: unknown stage token "${args[i]}".`);
              }
              return;
            }

            if (directive === "wait") {
              const wait = Number(args[0]);
              if (Number.isFinite(wait)) pendingWait += wait;
              else warnings.push(`Line ${lineNumber}: wait needs milliseconds.`);
              return;
            }

            if (directive === "grid") {
              const patch = gridPatchForVySu(args, warnings, lineNumber);
              if (patch) addCue({ action: "set", state: patch });
              return;
            }

            if (directive === "fullscreen" || directive === "theater") {
              addCue({ action: "fullscreen" });
              return;
            }

            if (directive === "exitfullscreen" || directive === "canvas") {
              addCue({ action: "exitFullscreen" });
              return;
            }

            if (directive === "caption" || directive === "say" || directive === "title") {
              const cue = { action: "caption", duration: 1500, fadeIn: 300, fadeOut: 300 };
              for (let index = 0; index < args.length; index += 1) {
                const arg = args[index];
                if (/^".*"$/.test(arg)) cue.text = arg.slice(1, -1);
                else {
                  const duration = parseVysuDuration(arg);
                  const alpha = parseVysuAlpha(arg);
                  const color = parseVysuColor(arg);
                  if (duration) Object.assign(cue, duration);
                  else if (/^\d+$/.test(arg)) cue.duration = Number(arg);
                  else if (["size", "font", "fontsize"].includes(arg.toLowerCase()) && Number.isFinite(Number(args[index + 1]))) {
                    cue.sizeRem = Number(args[index + 1]);
                    index += 1;
                  }
                  else if (arg.toLowerCase() === "fadein" && /^\d+$/.test(args[index + 1] || "")) {
                    cue.fadeIn = Number(args[index + 1]);
                    index += 1;
                  }
                  else if (arg.toLowerCase() === "fadeout" && /^\d+$/.test(args[index + 1] || "")) {
                    cue.fadeOut = Number(args[index + 1]);
                    index += 1;
                  }
                  else if (color) cue.color = color;
                  else if (alpha !== null) cue.opacity = alpha;
                }
              }
              if (!cue.text) warnings.push(`Line ${lineNumber}: caption needs quoted text.`);
              else addCue(cue);
              return;
            }

            if (["show", "reveal", "rollout", "fade", "hide"].includes(directive)) {
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const cue = { action: directive === "hide" ? "hide" : "reveal", target };
              if (directive === "rollout" || directive === "fade") cue.mode = directive;
              args.slice(1).forEach((arg) => {
                const lower = arg.toLowerCase();
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                else if (["instant", "fade", "stagger", "rollout"].includes(lower)) cue.mode = lower;
                else if (["ecliptic", "reverse-ecliptic", "reverse", "forward", "north-to-south", "south-to-north"].includes(lower)) cue.order = lower;
              });
              addCue(cue);
              return;
            }

            if (directive === "style") {
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const style = {};
              for (let i = 1; i < args.length; i += 1) {
                const key = args[i].toLowerCase();
                const next = args[i + 1];
                if (["color", "linecolor"].includes(key)) {
                  const color = parseVysuColor(next);
                  if (color) {
                    style[key === "linecolor" ? "lineColor" : "color"] = color;
                    i += 1;
                  } else warnings.push(`Line ${lineNumber}: ${args[i]} needs a color.`);
                } else if (["alpha", "opacity", "labelalpha"].includes(key)) {
                  const alpha = parseVysuAlpha(next);
                  if (alpha !== null) {
                    style[key === "labelalpha" ? "labelAlpha" : key] = alpha;
                    i += 1;
                  } else warnings.push(`Line ${lineNumber}: ${args[i]} needs alpha like %50 or .5.`);
                } else if (["fontsize", "font", "starsize", "pointsize"].includes(key)) {
                  const size = Number(next);
                  if (Number.isFinite(size)) {
                    if (key === "starsize") style.starSize = size;
                    else if (key === "pointsize") style.pointSize = size;
                    else style.fontSize = size;
                    i += 1;
                  } else warnings.push(`Line ${lineNumber}: ${args[i]} needs a numeric size.`);
                } else if (key === "font+" || key === "font-") {
                  const delta = Number.isFinite(Number(next)) ? Number(next) : 1;
                  style.fontSize = Math.max(1, (style.fontSize || 5) + (key === "font+" ? delta : -delta));
                  if (Number.isFinite(Number(next))) i += 1;
                } else {
                  const color = parseVysuColor(args[i]);
                  const alpha = parseVysuAlpha(args[i]);
                  if (color) style.color = color;
                  else if (alpha !== null) style.alpha = alpha;
                  else warnings.push(`Line ${lineNumber}: unsupported style token "${args[i]}".`);
                }
              }
              const patch = stylePatchForTarget(target, style);
              if (patch) addCue({ action: "set", state: patch });
              else warnings.push(`Line ${lineNumber}: no supported style knobs for ${target}.`);
              return;
            }

            if (directive === "flash") {
              const target = normalizeVysuTarget(args[0], warnings, lineNumber);
              if (!target) return;
              const cue = { action: "flash", target, duration: 1000 };
              args.slice(1).forEach((arg) => {
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                else if (/^\d+$/.test(arg)) cue.duration = Number(arg);
              });
              addCue(cue);
              return;
            }

            if (directive === "camera") {
              const cue = { action: "camera", camera: {}, duration: 1000 };
              for (let i = 0; i < args.length; i += 1) {
                const lower = args[i].toLowerCase();
                if (lower === "pos" || lower === "position") {
                  const vec = parseVysuVec3(args[i + 1]);
                  if (vec) {
                    cue.camera.position = vec;
                    i += 1;
                  }
                } else if (lower === "target") {
                  const vec = parseVysuVec3(args[i + 1]);
                  if (vec) {
                    cue.camera.target = vec;
                    i += 1;
                  }
                } else if (lower === "fov") {
                  const fov = Number(args[i + 1]);
                  if (Number.isFinite(fov)) {
                    cue.camera.fov = fov;
                    i += 1;
                  }
                } else {
                  const duration = parseVysuDuration(args[i]);
                  if (duration) cue.duration = duration.duration;
                  else if (/^\d+$/.test(args[i])) cue.duration = Number(args[i]);
                  else if (i === 0) warnings.push(`Line ${lineNumber}: camera preset "${args[i]}" is not implemented yet.`);
                }
              }
              if (Object.keys(cue.camera).length === 0) warnings.push(`Line ${lineNumber}: camera needs pos/target/fov.`);
              else addCue(cue);
              return;
            }

            if (directive === "travel" || directive === "epochtravel") {
              const from = Number(args[0]);
              const toIndex = args.findIndex((arg) => arg.toLowerCase() === "to");
              const to = Number(args[toIndex + 1]);
              const cue = { action: "epochTravel", from, to, duration: 5000 };
              args.forEach((arg, index) => {
                const duration = parseVysuDuration(arg);
                if (duration) cue.duration = duration.duration;
                if (arg.toLowerCase() === "step" && Number.isFinite(Number(args[index + 1]))) cue.step = Number(args[index + 1]);
              });
              if (!Number.isFinite(from) || toIndex < 0 || !Number.isFinite(to)) warnings.push(`Line ${lineNumber}: travel needs "from to to".`);
              else addCue(cue);
              return;
            }

            warnings.push(`Line ${lineNumber}: unknown directive "${tokens[0]}".`);
          });
        });

        return {
          story: {
            id: "vyoma-sutra-scratch",
            title: "VyomaSutra Scratch",
            version: 1,
            initial,
            cues,
          },
          warnings,
        };
      }

      // BEGIN VYOMASUTRA COMPILER
{
const VALID_ACTIONS = new Set([
  "caption",
  "set",
  "reveal",
  "hide",
  "camera",
  "epochTravel",
  "flash",
  "fullscreen",
  "exitFullscreen",
]);

const VALID_TARGETS = new Set([
  "eclipticGrid",
  "equatorialGrid",
  "eclipticNakSegments",
  "eclipticBand",
  "eclipticDividers",
  "eclipticLabels",
  "eclipticPoles",
  "stars",
  "nakshatraStars",
  "nakshatras",
  "nakshatraLines",
  "nakshatraLabels",
  "polarItems",
  "northPolarItems",
  "southPolarItems",
  "poleTrack",
  "precessionCircle",
  "seasonalFrame",
  "overlay",
  "referencePlanes",
  "eclipticPlane",
  "equatorialPlane",
  "nsAxis",
  "NEP",
  "SEP",
  "NP",
  "SP",
  "equator",
  "VE",
  "SS",
  "AE",
  "WS",
  "agastya",
  "thuban",
  "polaris",
  "matsya",
  "sisumara",
]);

const TARGET_ALIASES = {
  eclipticgrid: "eclipticGrid",
  eclgrid: "eclipticGrid",
  eclgridwire: "eclipticGrid",
  eclipticnaksegments: "eclipticNakSegments",
  eclipticnakssegments: "eclipticNakSegments",
  naksegments: "eclipticNakSegments",
  nakssegments: "eclipticNakSegments",
  eclipticsegments: "eclipticNakSegments",
  eclipticband: "eclipticBand",
  eclipticdividers: "eclipticDividers",
  sectordividers: "eclipticDividers",
  eclipticlabels: "eclipticLabels",
  sectorlabels: "eclipticLabels",
  eclipticpoles: "eclipticPoles",
  eclipticplane: "eclipticPlane",
  equatorialplane: "equatorialPlane",
  equatorialgrid: "equatorialGrid",
  equatorgrid: "equatorialGrid",
  eqgrid: "equatorialGrid",
  eq: "equatorialGrid",
  referenceplanes: "referencePlanes",
  refs: "referencePlanes",
  nsaxis: "nsAxis",
  axis: "nsAxis",
  nep: "NEP",
  sep: "SEP",
  np: "NP",
  sp: "SP",
  stars: "stars",
  nakshatrastars: "nakshatraStars",
  nakstars: "nakshatraStars",
  naksstars: "nakshatraStars",
  naks: "nakshatras",
  nak: "nakshatras",
  nakshatra: "nakshatras",
  nakshatras: "nakshatras",
  nakshatralines: "nakshatraLines",
  nakshatralabels: "nakshatraLabels",
  seasonalframe: "seasonalFrame",
  seasons: "seasonalFrame",
  rtus: "seasonalFrame",
  rtu: "seasonalFrame",
  poletrack: "poleTrack",
  polepath: "poleTrack",
  precessioncircle: "precessionCircle",
  precession: "precessionCircle",
  overlay: "overlay",
  polaritems: "polarItems",
  northpolaritems: "northPolarItems",
  northpolar: "northPolarItems",
  southpolaritems: "southPolarItems",
  southpolar: "southPolarItems",
  equator: "equator",
  ve: "VE",
  ss: "SS",
  ae: "AE",
  ws: "WS",
  agastya: "agastya",
  canopus: "agastya",
  thuban: "thuban",
  abhayadhruva: "thuban",
  polaris: "polaris",
  matsyadhruva: "polaris",
  matsya: "matsya",
  sisumara: "sisumara",
  shishumara: "sisumara",
  shimshumara: "sisumara",
};

const GROUP_TARGETS = {
  guides: ["equator", "ecliptic.circle", "nsAxis"],
};

const DOTTED_ALIASES = {
  eclipticcircle: "eclipticNakSegments",
  eclipticband: "eclipticBand",
  eclipticdividers: "eclipticDividers",
  eclipticlabels: "eclipticLabels",
  eclipticpoles: "eclipticPoles",
};

const SYMBOLIC_GROUP_ALIASES = {
  "*nak": ["nakshatraStars"],
  "*naks": ["nakshatraStars"],
  "*nakshatra": ["nakshatraStars"],
  "*nakshatras": ["nakshatraStars"],
  "$nak": ["nakshatraLines"],
  "$naks": ["nakshatraLines"],
  "$nakshatra": ["nakshatraLines"],
  "$nakshatras": ["nakshatraLines"],
  "@nak": ["nakshatraStars", "nakshatraLines"],
  "@naks": ["nakshatraStars", "nakshatraLines"],
  "@nakshatra": ["nakshatraStars", "nakshatraLines"],
  "@nakshatras": ["nakshatraStars", "nakshatraLines"],
};

const BLANK_UI = {
  showGrid: false,
  showEquatorialGrid: false,
  showReferencePlanes: false,
  showEclipticPlane: false,
  showEquatorialPlane: false,
  showNsAxis: false,
  showEclipticBand: false,
  showEclipticDividers: false,
  showEclipticLabels: false,
  showEclipticPoles: false,
  showStars: false,
  showNakshatraStars: false,
  showNakshatraLines: false,
  showNakshatraLabels: false,
  showPolarItems: false,
  showNorthPolarItems: false,
  showSouthPolarItems: false,
  showNEP: false,
  showSEP: false,
  showNP: false,
  showSP: false,
  showPoleTrack: false,
  showSeasonalFrame: false,
  showOverlay: false,
};

const COLOR_NAMES = new Set([
  "white",
  "black",
  "red",
  "orange",
  "yellow",
  "green",
  "blue",
  "cyan",
  "teal",
  "purple",
  "magenta",
  "pink",
  "gray",
  "grey",
  "gold",
  "brown",
]);

const STAGE2_COMMANDS = new Set(["draw", "blink", "glow"]);
const STAGE2_GROUPS = new Set(["sky", "poles"]);
const TRANSITION_MODES = new Set(["instant", "fade", "stagger", "rollout"]);
const TRANSITION_ORDERS = new Set(["default", "ecliptic", "reverse-ecliptic", "north-to-south", "south-to-north"]);
const DIRECTIONS = new Set(["forward", "reverse"]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function lineWarning(lineNumber, message) {
  return `Line ${lineNumber}: ${message}`;
}

function normalizeKey(value) {
  return String(value || "").replace(/[._-]/g, "").toLowerCase();
}

function parseMetadata(source) {
  const metadata = {};
  source.split(/\r?\n/).forEach((line) => {
    const match = line.match(/^\s*#\s*([a-zA-Z][\w-]*)\s*:\s*(.*?)\s*$/);
    if (match) metadata[match[1].toLowerCase()] = match[2];
  });
  return metadata;
}

function stripComment(line) {
  let quote = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') quote = !quote;
    if (!quote && ch === "#") {
      const hex = line.slice(i).match(/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(\b|\s|$)/);
      if (hex) {
        i += hex[1].length;
        continue;
      }
      return line.slice(0, i);
    }
  }
  return line;
}

function splitStatements(line) {
  const statements = [];
  let quote = false;
  let depth = 0;
  let start = 0;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') quote = !quote;
    if (!quote && ch === "{") depth += 1;
    if (!quote && ch === "}") depth = Math.max(0, depth - 1);
    if (!quote && depth === 0 && ch === ";") {
      const part = line.slice(start, i).trim();
      if (part) statements.push(part);
      start = i + 1;
    }
  }
  const tail = line.slice(start).trim();
  if (tail) statements.push(tail);
  return statements;
}

function tokenize(statement) {
  const tokens = [];
  const pattern = /"[^"]*"|\{|\}|,|\S+/g;
  let match;
  while ((match = pattern.exec(statement)) !== null) {
    tokens.push(match[0]);
  }
  return tokens;
}

function parseNumberToken(token) {
  const raw = String(token || "").replace(/y\/s$/i, "").replace(/[a-zA-Z]+$/g, "");
  const number = Number(raw);
  return Number.isFinite(number) ? number : null;
}

function parseDuration(token) {
  const raw = String(token || "").trim();
  const tuple = raw.match(/^(\d+(?:\.\d+)?):(\d*)?(?::(\d*)?)?$/);
  if (tuple) {
    const out = { duration: Number(tuple[1]) };
    if (tuple[2]) out.fadeIn = Number(tuple[2]);
    if (tuple[3]) out.fadeOut = Number(tuple[3]);
    return out;
  }
  const simple = raw.match(/^(-?\d+(?:\.\d+)?)(ms|s)?$/);
  if (!simple) return null;
  const scale = simple[2] === "s" ? 1000 : 1;
  return { duration: Math.round(Number(simple[1]) * scale) };
}

function parseSignedDuration(token) {
  const raw = String(token || "").trim();
  const match = raw.match(/^([+-])(.+)$/);
  if (!match) return null;
  const parsed = parseDuration(match[2]);
  if (!parsed) return null;
  return { sign: match[1], duration: parsed.duration };
}

function parseVec3(token) {
  const parts = String(token || "").split(",").map(Number);
  if (parts.length !== 3 || parts.some((part) => !Number.isFinite(part))) return null;
  return { x: parts[0], y: parts[1], z: parts[2] };
}

function parseVec2(token) {
  const parts = String(token || "").split(",").map(Number);
  if (parts.length !== 2 || parts.some((part) => !Number.isFinite(part))) return null;
  return { x: parts[0], y: parts[1] };
}

function parseAlpha(token) {
  const raw = String(token || "").trim();
  let value = null;
  if (/^%\d+(?:\.\d+)?$/.test(raw)) value = Number(raw.slice(1)) / 100;
  else if (/^\d+(?:\.\d+)?%$/.test(raw)) value = Number(raw.slice(0, -1)) / 100;
  else if (/^(?:0?\.\d+|1(?:\.0+)?)$/.test(raw)) value = Number(raw);
  else if (/^\d+(?:\.\d+)?$/.test(raw) && Number(raw) <= 1) value = Number(raw);
  return Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : null;
}

function parseColor(token) {
  const raw = String(token || "").trim();
  if (/^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$/.test(raw)) return raw;
  const lower = raw.toLowerCase();
  return COLOR_NAMES.has(lower) ? lower : null;
}

function durationFromArgs(args, index) {
  const arg = String(args[index] || "");
  if (arg.toLowerCase() === "over" && args[index + 1]) {
    const duration = parseDuration(args[index + 1]);
    return duration ? { ...duration, nextIndex: index + 1 } : null;
  }
  const duration = parseDuration(arg);
  return duration ? { ...duration, nextIndex: index } : null;
}

function resolveTargetAtom(token, lineNumber, warnings) {
  const raw = String(token || "").trim().replace(/,$/, "");
  if (!raw) {
    warnings.push(lineWarning(lineNumber, "missing target."));
    return [];
  }
  if (raw.includes("..")) {
    warnings.push(lineWarning(lineNumber, `target ranges are Stage 2 only: "${raw}".`));
    return [];
  }
  const symbolicGroup = SYMBOLIC_GROUP_ALIASES[normalizeKey(raw)];
  if (symbolicGroup) return symbolicGroup;
  if (/^[$*@][A-Za-z_][\w-]*$/.test(raw)) return [raw];
  if (GROUP_TARGETS[raw]) return GROUP_TARGETS[raw].flatMap((target) => resolveTargetAtom(target, lineNumber, warnings));
  if (STAGE2_GROUPS.has(raw)) {
    warnings.push(lineWarning(lineNumber, `group target "${raw}" is Stage 2 only; no canonical expansion yet.`));
    return [];
  }
  const dotted = DOTTED_ALIASES[normalizeKey(raw)];
  const target = dotted || TARGET_ALIASES[normalizeKey(raw)] || raw;
  if (!VALID_TARGETS.has(target)) {
    warnings.push(lineWarning(lineNumber, `unsupported target "${raw}".`));
    return [];
  }
  return [target];
}

function readTargetList(args, lineNumber, warnings) {
  const atoms = [];
  let i = 0;
  while (i < args.length) {
    let token = args[i];
    const lower = String(token).toLowerCase();
    if (token === "," || lower === "and") {
      i += 1;
      continue;
    }
    if (isPropertyStart(args, i)) break;
    const hadTrailingComma = String(token).endsWith(",");
    if (hadTrailingComma) token = String(token).slice(0, -1);
    const resolved = resolveTargetAtom(token, lineNumber, warnings);
    if (resolved.length) atoms.push(...resolved);
    i += 1;
    const next = args[i];
    if (!next || hadTrailingComma || next === "," || String(next).toLowerCase() === "and" || isPropertyStart(args, i)) continue;
    if (resolved.length) {
      warnings.push(lineWarning(lineNumber, `target lists need commas or "and"; stopped before "${next}".`));
    }
    break;
  }
  return { targets: atoms, nextIndex: i };
}

function isPropertyStart(args, index) {
  const lower = String(args[index] || "").toLowerCase();
  if (["over", "instant", "fade", "stagger", "rollout", "default", "ecliptic", "reverse-ecliptic", "north-to-south", "south-to-north", "forward", "reverse", "ease", "step", "rate", "gap", "color", "linecolor", "alpha", "opacity", "labelalpha", "fontsize", "font", "starsize", "pointsize", "font+", "font-", "size", "fadein", "fadeout", "screen", "dx", "dy", "class"].includes(lower)) return true;
  if (/^\d+(?:\.\d+)?(?::|\s*$)/.test(lower)) return true;
  if (/^\d+(?:\.\d+)?(ms|s)?$/.test(lower)) return true;
  if (/^\d+x$/i.test(lower)) return true;
  if (parseColor(args[index]) || parseAlpha(args[index]) !== null) return true;
  return false;
}

function put(patch, path, value) {
  let cursor = patch;
  path.slice(0, -1).forEach((key) => {
    if (!cursor[key]) cursor[key] = {};
    cursor = cursor[key];
  });
  cursor[path[path.length - 1]] = value;
}

function mergePatch(target, patch) {
  Object.entries(patch || {}).forEach(([key, value]) => {
    if (value && typeof value === "object" && !Array.isArray(value) && target[key] && typeof target[key] === "object" && !Array.isArray(target[key])) {
      mergePatch(target[key], value);
    } else {
      target[key] = clone(value);
    }
  });
  return target;
}

function stylePatchForTarget(target, style) {
  const patch = {};
  const color = style.color || style.lineColor;
  const alpha = style.alpha ?? style.opacity;
  const fontSize = style.fontSize;
  const pointSize = style.pointSize ?? style.starSize;
  if (target === "eclipticGrid") {
    if (color) {
      put(patch, ["grid", "parallelColor"], color);
      put(patch, ["grid", "meridianColor"], color);
    }
    if (alpha !== undefined) {
      put(patch, ["grid", "parallelOpacity"], alpha);
      put(patch, ["grid", "meridianOpacity"], alpha);
    }
  } else if (target === "equatorialGrid") {
    if (color) put(patch, ["grid", "equatorialColor"], color);
    if (alpha !== undefined) put(patch, ["grid", "equatorialOpacity"], alpha);
  } else if (target === "nsAxis") {
    if (color) put(patch, ["reference", "nsAxisColor"], color);
    if (alpha !== undefined) put(patch, ["reference", "nsAxisOpacity"], alpha);
  } else if (target === "eclipticPlane") {
    if (color) put(patch, ["reference", "eclipticPlaneColor"], color);
    if (alpha !== undefined) put(patch, ["reference", "eclipticPlaneOpacity"], alpha);
  } else if (target === "equatorialPlane") {
    if (color) put(patch, ["reference", "equatorialPlaneColor"], color);
    if (alpha !== undefined) put(patch, ["reference", "equatorialPlaneOpacity"], alpha);
  } else if (target === "stars" || target === "nakshatraStars") {
    if (alpha !== undefined) put(patch, ["stars", "opacity"], alpha);
    if (pointSize !== undefined) put(patch, ["stars", "size"], pointSize);
  } else if (target === "nakshatras" || target === "nakshatraLines" || target === "nakshatraLabels") {
    if (color) put(patch, ["nakshatras", "color"], color);
    if (alpha !== undefined) put(patch, ["nakshatras", "opacity"], alpha);
    if (fontSize !== undefined) put(patch, ["nakshatras", "labelSize"], fontSize);
    if (style.labelAlpha !== undefined) put(patch, ["nakshatras", "labelOpacity"], style.labelAlpha);
  } else if (target === "polarItems" || target === "northPolarItems" || target === "southPolarItems") {
    if (color) put(patch, ["polarItems", "color"], color);
    if (alpha !== undefined) put(patch, ["polarItems", "opacity"], alpha);
    if (fontSize !== undefined) put(patch, ["polarItems", "labelSize"], fontSize);
    if (style.labelAlpha !== undefined) put(patch, ["polarItems", "labelOpacity"], style.labelAlpha);
  } else if (target === "poleTrack" || target === "precessionCircle") {
    if (color) put(patch, ["poleTrack", "color"], color);
    if (alpha !== undefined) put(patch, ["poleTrack", "opacity"], alpha);
    if (fontSize !== undefined) put(patch, ["poleTrack", "trackLabelSize"], fontSize);
  } else if (target === "seasonalFrame") {
    if (color) put(patch, ["seasonal", "equatorColor"], color);
    if (alpha !== undefined) put(patch, ["seasonal", "equatorOpacity"], alpha);
    if (fontSize !== undefined) put(patch, ["seasonal", "markerLabelSize"], fontSize);
    if (style.labelAlpha !== undefined) put(patch, ["seasonal", "markerLabelOpacity"], style.labelAlpha);
  } else if (target === "eclipticNakSegments" || target === "eclipticBand" || target === "eclipticLabels") {
    if (color) put(patch, ["ecliptic", "circleColor"], color);
    if (alpha !== undefined) put(patch, ["ecliptic", "circleOpacity"], alpha);
    if (fontSize !== undefined) put(patch, ["ecliptic", "sectorLabelSize"], fontSize);
    if (style.labelAlpha !== undefined) put(patch, ["ecliptic", "sectorLabelOpacity"], style.labelAlpha);
  } else if (target === "overlay") {
    if (alpha !== undefined) put(patch, ["overlay", "opacity"], alpha);
    if (fontSize !== undefined) put(patch, ["overlay", "fontSizeRem"], fontSize);
  }
  return Object.keys(patch).length ? patch : null;
}

function gridPatch(args, lineNumber, warnings) {
  if (args.length < 2) {
    warnings.push(lineWarning(lineNumber, "grid needs kind and step."));
    return null;
  }
  const kind = String(args[0]).toLowerCase();
  const step = Number(args[1]);
  if (!Number.isFinite(step)) {
    warnings.push(lineWarning(lineNumber, "grid step must be numeric."));
    return null;
  }
  const color = parseColor(args[2]);
  const patch = { grid: {}, ui: {} };
  if (kind === "ecliptic" || kind === "ecl") {
    patch.grid.eclipticStepDeg = step;
    if (color) {
      patch.grid.parallelColor = color;
      patch.grid.meridianColor = color;
    }
    patch.ui.showGrid = true;
  } else if (kind === "equatorial" || kind === "equator" || kind === "eq") {
    patch.grid.equatorialStepDeg = step;
    if (color) patch.grid.equatorialColor = color;
    patch.ui.showEquatorialGrid = true;
  } else {
    warnings.push(lineWarning(lineNumber, "grid kind must be ecliptic or equatorial."));
    return null;
  }
  return patch;
}

function parseTiming(tokens) {
  if (!tokens.length) return { timing: null, tokens };
  const first = String(tokens[0]).toLowerCase();
  if (first === "at" && tokens[1]) {
    const duration = parseDuration(tokens[1]);
    return duration ? { timing: { kind: "at", value: duration.duration }, tokens: tokens.slice(2) } : { timing: null, tokens };
  }
  if (first === "after" && tokens[1]) {
    const duration = parseDuration(tokens[1]);
    return duration ? { timing: { kind: "after", value: duration.duration }, tokens: tokens.slice(2) } : { timing: null, tokens };
  }
  const signed = parseSignedDuration(tokens[0]);
  if (signed) return { timing: { kind: "after", value: signed.sign === "-" ? -signed.duration : signed.duration }, tokens: tokens.slice(1) };
  return { timing: null, tokens };
}

function screenLocation(args, index, cue, lineNumber, warnings) {
  const anchor = args[index + 1];
  if (!anchor) {
    warnings.push(lineWarning(lineNumber, "screen needs an anchor."));
    return index;
  }
  cue.screen = anchor;
  return index + 1;
}

function parseQuotedText(token) {
  return /^"[^"]*"$/.test(String(token || "")) ? String(token).slice(1, -1) : null;
}

function applyStageArgs(args, patch, lineNumber, warnings) {
  for (let i = 0; i < args.length; i += 1) {
    const arg = String(args[i]).toLowerCase();
    if (arg === "blank") {
      if (!patch.ui) patch.ui = {};
      Object.assign(patch.ui, BLANK_UI);
    } else if (arg === "all") {
      warnings.push(lineWarning(lineNumber, 'stage "all" is not implemented; use explicit show commands.'));
    } else if (arg === "night" || arg === "twilight" || arg === "day") {
      patch.lightPreset = arg;
    } else if ((arg === "year" || arg === "epoch") && args[i + 1]) {
      const year = Number(args[i + 1]);
      if (Number.isFinite(year)) {
        patch.epochYear = Math.trunc(year);
        i += 1;
      } else {
        warnings.push(lineWarning(lineNumber, `stage ${arg} needs numeric value.`));
      }
    } else if (arg) {
      warnings.push(lineWarning(lineNumber, `unknown stage token "${args[i]}".`));
    }
  }
}

function removeEmptyInitial(initial) {
  const out = clone(initial);
  if (out.ui && Object.keys(out.ui).length === 0) delete out.ui;
  return Object.keys(out).length ? out : null;
}

compileVyomaSutra = function compileVyomaSutraStage1(source, options = {}) {
  const metadata = parseMetadata(source);
  const storyId = options.storyId || "vyoma-sutra-scratch";
  const warnings = [];
  const story = {
    id: storyId,
    title: options.title || metadata.title || (storyId === "vyoma-sutra-scratch" ? "VyomaSutra Scratch" : storyId.replace(/-/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase())),
    version: Number(metadata.version || 1),
    vysu: source.replace(/\s*$/, "\n"),
    cues: [],
  };
  if (/^(1|true|yes|y)$/i.test(metadata.featured || "")) story.featured = true;
  if (metadata.group) story.group = metadata.group;
  if (metadata.tags) story.tags = metadata.tags.split(",").map((tag) => tag.trim()).filter(Boolean);
  if (metadata.order && Number.isFinite(Number(metadata.order))) story.order = Number(metadata.order);

  const initial = { ui: {} };
  let defaultBlockSeq = 0;
  const timingStack = [{ base: 0, time: 0, seq: 0 }];
  let emitted = 0;
  let activeCommand = null;

  const current = () => timingStack[timingStack.length - 1];
  const inTimedBlock = () => timingStack.length > 1;
  const scheduleCommandAt = (timing) => {
    if (timing?.kind === "at") return current().base + timing.value;
    if (timing?.kind === "after") {
      current().time += timing.value;
      return current().base + current().time;
    }
    if (inTimedBlock()) current().time += current().seq || 0;
    return current().base + current().time;
  };
  const commandAt = () => {
    if (!activeCommand) return scheduleCommandAt(null);
    if (activeCommand.at === null) activeCommand.at = scheduleCommandAt(activeCommand.timing);
    return activeCommand.at;
  };
  const addCue = (cue, timing = null) => {
    const at = timing ? scheduleCommandAt(timing) : commandAt();
    story.cues.push({ at, ...cue });
    emitted += 1;
    return at;
  };
  const addCueAt = (cue, at) => {
    story.cues.push({ at, ...cue });
    emitted += 1;
  };
  const applyStage = (args, lineNumber, timing = null) => {
    const patch = { ui: {} };
    applyStageArgs(args, patch, lineNumber, warnings);
    if (!patch.ui || Object.keys(patch.ui).length === 0) delete patch.ui;
    if (emitted === 0 && !timing && !inTimedBlock()) mergePatch(initial, patch);
    else if (Object.keys(patch).length) addCue({ action: "set", state: patch });
  };

  const compileCommand = (rawTokens, lineNumber, inheritedTiming = null) => {
    const parsedTiming = parseTiming(rawTokens);
    const timing = parsedTiming.timing || inheritedTiming;
    const tokens = parsedTiming.tokens;
    if (!tokens.length) return;
    const directive = String(tokens[0]).toLowerCase();
    const args = tokens.slice(1);
    const previousCommand = activeCommand;
    activeCommand = { timing, at: null };

    try {
      if (STAGE2_COMMANDS.has(directive)) {
        warnings.push(lineWarning(lineNumber, `${tokens[0]} is Stage 2 only and was ignored.`));
        return;
      }
      if (directive === "effects") {
        warnings.push(lineWarning(lineNumber, "effects defaults are accepted as warnings only in Stage 1."));
        return;
      }
      if (directive === "defaults") {
        warnings.push(lineWarning(lineNumber, "defaults are accepted as warnings only in Stage 1."));
        return;
      }
      if (directive === "stage" || directive === "scene") {
        applyStage(args, lineNumber, timing);
        return;
      }
      if (directive === "seq" || directive === "sequence") {
        const duration = parseDuration(args[0]);
        if (!duration) {
          warnings.push(lineWarning(lineNumber, "seq needs a duration."));
        } else if (inTimedBlock()) {
          current().seq = duration.duration;
        } else {
          defaultBlockSeq = duration.duration;
        }
        return;
      }
      if (directive === "wait") {
        const duration = parseDuration(args[0]);
        if (duration) current().time += duration.duration;
        else warnings.push(lineWarning(lineNumber, "wait needs a duration."));
        return;
      }
      if (directive === "grid") {
      const patch = gridPatch(args, lineNumber, warnings);
      if (patch) addCue({ action: "set", state: patch });
      return;
    }
    if (directive === "fullscreen" || directive === "theater") {
      addCue({ action: "fullscreen" });
      return;
    }
    if (directive === "exitfullscreen" || directive === "canvas") {
      addCue({ action: "exitFullscreen" });
      return;
    }
    if (directive === "caption" || directive === "say" || directive === "title") {
      const cue = { action: "caption", duration: 1200, fadeIn: 300, fadeOut: 300 };
      for (let i = 0; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        const text = parseQuotedText(args[i]);
        const duration = durationFromArgs(args, i);
        const color = parseColor(args[i]);
        const alpha = parseAlpha(args[i]);
        if (text !== null) cue.text = text;
        else if (duration) {
          cue.duration = duration.duration;
          if (duration.fadeIn !== undefined) cue.fadeIn = duration.fadeIn;
          if (duration.fadeOut !== undefined) cue.fadeOut = duration.fadeOut;
          i = duration.nextIndex;
        } else if (lower === "fade" && args[i + 1]) {
          const fade = String(args[i + 1]).match(/^(\d+)(?::(\d+))?$/);
          if (fade) {
            cue.fadeIn = Number(fade[1]);
            cue.fadeOut = Number(fade[2] || fade[1]);
            i += 1;
          }
        } else if ((lower === "fadein" || lower === "fadeout") && args[i + 1]) {
          const fade = parseDuration(args[i + 1]);
          if (fade) {
            cue[lower === "fadein" ? "fadeIn" : "fadeOut"] = fade.duration;
            i += 1;
          }
        } else if ((lower === "size" || lower === "font") && Number.isFinite(Number(args[i + 1]))) {
          cue.sizeRem = Number(args[i + 1]);
          i += 1;
        } else if (/^\d+(?:\.\d+)?px$/.test(lower)) {
          cue.sizePx = Number(lower.slice(0, -2));
        } else if (lower === "screen") {
          i = screenLocation(args, i, cue, lineNumber, warnings);
        } else if ((lower === "dx" || lower === "dy") && Number.isFinite(Number(args[i + 1]))) {
          cue[lower] = Number(args[i + 1]);
          i += 1;
        } else if (color) cue.color = color;
        else if (alpha !== null) cue.opacity = alpha;
        else warnings.push(lineWarning(lineNumber, `unsupported caption token "${args[i]}".`));
      }
      if (!cue.text) warnings.push(lineWarning(lineNumber, "caption needs quoted text."));
      else addCue(cue);
      return;
    }
    if (["show", "reveal", "rollout", "fade", "hide"].includes(directive)) {
      const targetList = readTargetList(args, lineNumber, warnings);
      if (!targetList.targets.length) return;
      const cueBase = { action: directive === "hide" ? "hide" : "reveal" };
      if (directive === "rollout" || directive === "fade") cueBase.mode = directive;
      for (let i = targetList.nextIndex; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        const duration = durationFromArgs(args, i);
        if (duration) {
          cueBase.duration = duration.duration;
          if (duration.fadeIn !== undefined || duration.fadeOut !== undefined) {
            warnings.push(lineWarning(lineNumber, `extra tuple fields on ${directive} duration were ignored.`));
          }
          i = duration.nextIndex;
        } else if (TRANSITION_MODES.has(lower)) cueBase.mode = lower;
        else if (TRANSITION_ORDERS.has(lower)) cueBase.order = lower;
        else if (DIRECTIONS.has(lower)) cueBase.direction = lower;
        else if (lower === "ease" && args[i + 1]) {
          cueBase.ease = args[i + 1];
          i += 1;
        } else warnings.push(lineWarning(lineNumber, `unsupported transition token "${args[i]}".`));
      }
      targetList.targets.forEach((target) => addCue({ ...cueBase, target }));
      return;
    }
    if (directive === "style") {
      const targetList = readTargetList(args, lineNumber, warnings);
      if (!targetList.targets.length) return;
      const style = {};
      for (let i = targetList.nextIndex; i < args.length; i += 1) {
        const key = String(args[i]).toLowerCase();
        const next = args[i + 1];
        const color = parseColor(args[i]);
        const alpha = parseAlpha(args[i]);
        if (["color", "linecolor"].includes(key)) {
          const parsed = parseColor(next);
          if (parsed) {
            style[key === "linecolor" ? "lineColor" : "color"] = parsed;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, `${args[i]} needs a color.`));
        } else if (["alpha", "opacity", "labelalpha"].includes(key)) {
          const parsed = parseAlpha(next);
          if (parsed !== null) {
            style[key === "labelalpha" ? "labelAlpha" : key] = parsed;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, `${args[i]} needs alpha like %50 or .5.`));
        } else if (["fontsize", "font", "starsize", "pointsize"].includes(key)) {
          const size = Number(next);
          if (Number.isFinite(size)) {
            if (key === "starsize") style.starSize = size;
            else if (key === "pointsize") style.pointSize = size;
            else style.fontSize = size;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, `${args[i]} needs a numeric size.`));
        } else if (key === "font+" || key === "font-") {
          const delta = Number.isFinite(Number(next)) ? Number(next) : 1;
          style.fontSize = Math.max(1, (style.fontSize || 5) + (key === "font+" ? delta : -delta));
          if (Number.isFinite(Number(next))) i += 1;
        } else if (color) style.color = color;
        else if (alpha !== null) style.alpha = alpha;
        else warnings.push(lineWarning(lineNumber, `unsupported style token "${args[i]}".`));
      }
      targetList.targets.forEach((target) => {
        const patch = stylePatchForTarget(target, style);
        if (patch) addCue({ action: "set", state: patch });
        else warnings.push(lineWarning(lineNumber, `no supported style knobs for ${target}.`));
      });
      return;
    }
    if (directive === "flash" || directive === "pulse") {
      const targetList = readTargetList(args, lineNumber, warnings);
      if (!targetList.targets.length) return;
      const cue = { action: "flash", duration: 900 };
      let repeat = directive === "pulse" ? 3 : 1;
      let gap = 120;
      for (let i = targetList.nextIndex; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        const duration = durationFromArgs(args, i);
        if (duration) {
          cue.duration = duration.duration;
          i = duration.nextIndex;
        } else if (/^\d+x$/i.test(lower)) repeat = Math.max(1, Number(lower.slice(0, -1)));
        else if (lower === "gap" && args[i + 1]) {
          const parsed = parseDuration(args[i + 1]);
          if (parsed) {
            gap = parsed.duration;
            i += 1;
          }
        } else {
          const color = parseColor(args[i]);
          const alpha = parseAlpha(args[i]);
          if (color) cue.color = color;
          else if (alpha !== null) cue.opacity = alpha;
          else warnings.push(lineWarning(lineNumber, `unsupported effect token "${args[i]}".`));
        }
      }
      const firstAt = commandAt();
      for (let r = 0; r < repeat; r += 1) {
        targetList.targets.forEach((target) => addCueAt({ ...cue, target }, firstAt + gap * r));
      }
      return;
    }
    if (directive === "camera" || directive === "move" || directive === "cut") {
      const cue = { action: "camera", camera: {}, duration: directive === "cut" ? 0 : 1000 };
      for (let i = 0; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        if (lower === "pos" || lower === "position") {
          const vec = parseVec3(args[i + 1]);
          if (vec) {
            cue.camera.position = vec;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, "camera pos needs x,y,z."));
        } else if (lower === "target") {
          const vec = parseVec3(args[i + 1]);
          if (vec) {
            cue.camera.target = vec;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, "camera target needs x,y,z."));
        } else if (lower === "fov" && args[i + 1]) {
          const fov = Number(args[i + 1]);
          if (Number.isFinite(fov)) {
            cue.camera.fov = fov;
            i += 1;
          } else warnings.push(lineWarning(lineNumber, "camera fov needs a number."));
        } else {
          const duration = durationFromArgs(args, i);
          if (duration) {
            cue.duration = duration.duration;
            i = duration.nextIndex;
          } else if (i === 0) warnings.push(lineWarning(lineNumber, `camera preset "${args[i]}" is not implemented yet.`));
          else warnings.push(lineWarning(lineNumber, `unsupported camera token "${args[i]}".`));
        }
      }
      if (!Object.keys(cue.camera).length) warnings.push(lineWarning(lineNumber, "camera needs pos, target, or fov."));
      else if (emitted === 0 && !timing && !inTimedBlock()) mergePatch(initial, { camera: cue.camera });
      else addCue(cue);
      return;
    }
    if (directive === "travel" || directive === "epochtravel") {
      let argsStart = 0;
      if (["year", "epoch"].includes(String(args[0] || "").toLowerCase())) argsStart = 1;
      const from = Number(args[argsStart]);
      const toIndex = args.findIndex((arg) => String(arg).toLowerCase() === "to");
      const to = Number(args[toIndex + 1]);
      const cue = { action: "epochTravel", from: Math.trunc(from), to: Math.trunc(to), duration: 5000, step: 100 };
      for (let i = argsStart + 1; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        const duration = durationFromArgs(args, i);
        if (duration) {
          cue.duration = duration.duration;
          i = duration.nextIndex;
        } else if (lower === "step" && args[i + 1]) {
          const step = parseNumberToken(args[i + 1]);
          if (step !== null) {
            cue.step = step;
            i += 1;
          }
        } else if (lower === "rate" && args[i + 1]) {
          cue.rate = args[i + 1];
          i += 1;
        }
      }
      if (!Number.isFinite(from) || toIndex < 0 || !Number.isFinite(to)) warnings.push(lineWarning(lineNumber, 'travel needs "FROM to TO".'));
      else addCue(cue);
      return;
    }
    if (directive === "label") {
      const id = args[0];
      const text = parseQuotedText(args[1]);
      if (!id || text === null) {
        warnings.push(lineWarning(lineNumber, "label needs an id and quoted text."));
        return;
      }
      const label = { id, text };
      for (let i = 2; i < args.length; i += 1) {
        const lower = String(args[i]).toLowerCase();
        const color = parseColor(args[i]);
        const alpha = parseAlpha(args[i]);
        if (lower === "at" && String(args[i + 1]).toLowerCase() === "screen") {
          label.mode = "screen";
          label.screen = args[i + 2];
          i += 2;
        } else if (lower === "at" && String(args[i + 1]).toLowerCase() === "target") {
          const target = resolveTargetAtom(args[i + 2], lineNumber, warnings)[0];
          if (target) {
            label.mode = "target";
            label.target = target;
          }
          i += 2;
        } else if ((lower === "dx" || lower === "dy") && Number.isFinite(Number(args[i + 1]))) {
          label[lower] = Number(args[i + 1]);
          i += 1;
        } else if (lower === "class" && args[i + 1]) {
          label.className = args[i + 1];
          i += 1;
        } else if ((lower === "size" || lower === "font") && Number.isFinite(Number(args[i + 1]))) {
          label.sizeRem = Number(args[i + 1]);
          i += 1;
        } else if (parseVec2(args[i])) {
          const vec = parseVec2(args[i]);
          label.dx = vec.x;
          label.dy = vec.y;
        } else if (color) label.color = color;
        else if (alpha !== null) label.opacity = alpha;
        else warnings.push(lineWarning(lineNumber, `unsupported label token "${args[i]}".`));
      }
      addCue({ action: "set", state: { labels: { [id]: label } } });
      return;
    }
    if (directive === "clear") {
      const lower = String(args[0] || "").toLowerCase();
      if (lower === "labels") addCue({ action: "set", state: { labels: {} } });
      else if (lower === "label" && args[1]) addCue({ action: "set", state: { labels: { [args[1]]: null } } });
      else warnings.push(lineWarning(lineNumber, 'clear needs "labels" or "label ID".'));
      return;
    }
      warnings.push(lineWarning(lineNumber, `unknown directive "${tokens[0]}".`));
    } finally {
      activeCommand = previousCommand;
    }
  };

  const compileStatement = (statement, lineNumber) => {
    const tokens = tokenize(statement);
    if (!tokens.length) return;
    const timed = parseTiming(tokens);
    if (timed.timing && timed.tokens[0] === "{") {
      const close = timed.tokens.lastIndexOf("}");
      if (close < 0) {
        warnings.push(lineWarning(lineNumber, "timed block needs closing }."));
        return;
      }
      const body = timed.tokens.slice(1, close).join(" ");
      const parent = current();
      const blockBase = scheduleCommandAt(timed.timing);
      const blockFrame = { base: blockBase, time: 0, seq: defaultBlockSeq };
      timingStack.push(blockFrame);
      splitStatements(body).forEach((part) => compileCommand(tokenize(part), lineNumber, null));
      timingStack.pop();
      parent.time = Math.max(parent.time, blockBase + blockFrame.time - parent.base);
      return;
    }
    compileCommand(tokens, lineNumber, null);
  };

  let block = null;
  for (const [index, line] of source.split(/\r?\n/).entries()) {
    if (/^\s*__(?:END|DATA)__\s*$/.test(line)) break;
    if (/^\s*#\s*[a-zA-Z][\w-]*\s*:/.test(line)) continue;
    const uncommented = stripComment(line).trim();
    if (!uncommented) continue;

    if (block) {
      if (uncommented === "}") {
        compileStatement(`${block.header} { ${block.body.join("; ")} }`, block.lineNumber);
        block = null;
      } else {
        block.body.push(uncommented);
      }
      continue;
    }

    const blockStart = uncommented.match(/^((?:at|after)\s+\S+|[+-][^\s{]+)\s*\{\s*$/);
    if (blockStart) {
      block = { header: blockStart[1], body: [], lineNumber: index + 1 };
      continue;
    }

    splitStatements(uncommented).forEach((statement) => compileStatement(statement, index + 1));
  }
  if (block) warnings.push(lineWarning(block.lineNumber, "timed block needs closing }."));

  const cleanedInitial = removeEmptyInitial(initial);
  if (cleanedInitial) story.initial = cleanedInitial;
  if (warnings.length) story.warnings = warnings;
  validateStory(story);
  return { story, warnings };
}

function validateStory(story) {
  ["id", "title", "version", "cues"].forEach((key) => {
    if (!(key in story)) throw new Error(`story missing required key: ${key}`);
  });
  if (!Array.isArray(story.cues)) throw new Error("story cues must be an array.");
  story.cues.forEach((cue, index) => {
    if (!cue || typeof cue !== "object" || Array.isArray(cue)) throw new Error(`cue ${index} must be an object.`);
    if (!("at" in cue) && !("after" in cue)) throw new Error(`cue ${index} needs at or after.`);
    if (!VALID_ACTIONS.has(cue.action)) throw new Error(`cue ${index} has unknown action ${JSON.stringify(cue.action)}.`);
    if (cue.action === "caption" && !("text" in cue)) throw new Error(`cue ${index} caption needs text.`);
    if (cue.action === "set" && !("state" in cue)) throw new Error(`cue ${index} set needs state.`);
    if ((cue.action === "reveal" || cue.action === "hide" || cue.action === "flash") && !("target" in cue)) throw new Error(`cue ${index} ${cue.action} needs target.`);
    if ((cue.action === "reveal" || cue.action === "hide" || cue.action === "flash") && typeof cue.target === "string" && !/^[$*@]/.test(cue.target) && !VALID_TARGETS.has(cue.target)) {
      throw new Error(`cue ${index} has unknown target ${JSON.stringify(cue.target)}.`);
    }
    if (cue.action === "camera" && !cue.camera) throw new Error(`cue ${index} camera needs camera.`);
    if (cue.action === "epochTravel") {
      ["from", "to", "duration"].forEach((key) => {
        if (!(key in cue)) throw new Error(`cue ${index} epochTravel needs ${key}.`);
      });
    }
  });
  return story;
}

function compileVyomaSutraFile(source, storyId) {
  return compileVyomaSutra(source, { storyId }).story;
}

}
// END VYOMASUTRA COMPILER

      function mergeSettings(target, patch) {
        Object.entries(patch || {}).forEach(([key, value]) => {
          if (value && typeof value === "object" && !Array.isArray(value)) {
            if (!target[key] || typeof target[key] !== "object" || Array.isArray(target[key])) {
              target[key] = {};
            }
            mergeSettings(target[key], value);
          } else {
            target[key] = value;
          }
        });
        return target;
      }

      function setStoryCaption(text, visible, transitionMs = 260, opts = null) {
        if (!storyCaption) return;
        storyCaption.style.transitionDuration = `${Math.max(0, transitionMs)}ms`;
        storyCaption.textContent = text || "";
        storyCaption.style.color = opts?.color || "";
        storyCaption.style.fontSize = opts?.sizeRem ? `${opts.sizeRem}rem` : "";
        storyCaption.classList.toggle("visible", Boolean(visible && text));
      }

      function clearStoryLabels() {
        storyLabels = {};
        if (storyLabelLayer) storyLabelLayer.innerHTML = "";
      }

      function applyStoryLabelsPatch(labelsPatch) {
        if (!labelsPatch || typeof labelsPatch !== "object") return;
        if (Object.keys(labelsPatch).length === 0) {
          clearStoryLabels();
          return;
        }
        Object.entries(labelsPatch).forEach(([id, label]) => {
          if (label === null) delete storyLabels[id];
          else storyLabels[id] = { ...(storyLabels[id] || {}), ...(label || {}), id };
        });
        renderStoryLabels();
      }

      function storyLabelAnchor(anchor) {
        const key = String(anchor || "5").toUpperCase();
        return {
          "1": [16, 84], "2": [50, 84], "3": [84, 84],
          "4": [16, 50], "5": [50, 50], "6": [84, 50],
          "7": [16, 16], "8": [50, 16], "9": [84, 16],
          SW: [16, 84], S: [50, 84], SE: [84, 84],
          W: [16, 50], C: [50, 50], E: [84, 50],
          NW: [16, 16], N: [50, 16], NE: [84, 16],
        }[key] || [50, 50];
      }

      function storyTargetObject(target) {
        if (target === "NP") return poleDot;
        if (target === "SP") return southPoleDot;
        if (["VE", "SS", "AE", "WS"].includes(target)) {
          return seasonalMarkerRefs.find((entry) => entry.key === target)?.mesh || null;
        }
        return transitionDescriptorsForTarget(target)?.[0]?.items?.[0]?.object || null;
      }

      function renderStoryLabels() {
        if (!storyLabelLayer) return;
        storyLabelLayer.innerHTML = "";
        Object.values(storyLabels).forEach((label) => {
          const element = document.createElement("div");
          element.className = `three-story-label ${label.className || ""}`;
          element.dataset.labelId = label.id;
          element.textContent = label.text || "";
          element.style.color = label.color || "";
          element.style.opacity = label.opacity ?? "";
          element.style.fontSize = label.sizeRem ? `${label.sizeRem}rem` : "";
          storyLabelLayer.appendChild(element);
        });
        updateStoryLabels();
      }

      function updateStoryLabels() {
        if (!storyLabelLayer || !camera || !renderer) return;
        storyLabelLayer.querySelectorAll(".three-story-label").forEach((element) => {
          const label = storyLabels[element.dataset.labelId];
          if (!label) return;
          let x = 50;
          let y = 50;
          let visible = true;
          if (label.mode === "target" && label.target) {
            const object = storyTargetObject(label.target);
            if (object) {
              const pos = new THREE.Vector3();
              object.getWorldPosition(pos);
              pos.project(camera);
              visible = pos.z >= -1 && pos.z <= 1;
              x = ((pos.x + 1) / 2) * 100;
              y = ((1 - pos.y) / 2) * 100;
            } else {
              visible = false;
            }
          } else {
            [x, y] = storyLabelAnchor(label.screen);
          }
          element.style.left = `calc(${x}% + ${Number(label.dx || 0)}px)`;
          element.style.top = `calc(${y}% + ${Number(label.dy || 0)}px)`;
          element.style.display = visible ? "" : "none";
        });
      }

      function stopStory(clearCaption = true) {
        activeStoryTimers.splice(0).forEach((timer) => window.clearTimeout(timer));
        if (activeStoryFrame !== null) {
          window.cancelAnimationFrame(activeStoryFrame);
          activeStoryFrame = null;
        }
        activeStoryId = null;
        activeTransitionTargets.clear();
        activeTransitionObjects.clear();
        targetVisibilityOverrides.clear();
        focusedPolarTargets.north.clear();
        focusedPolarTargets.south.clear();
        focusedSeasonalTargets.clear();
        clearStoryLabels();
        applyOrbitMode();
        if (clearCaption) setStoryCaption("", false);
        if (storyStrip) {
          storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {
            button.classList.remove("active");
          });
        }
      }

      function setThreeFullscreen(enabled) {
        if (!container) return;
        if (enabled) {
          if (container.requestFullscreen) {
            container.requestFullscreen().catch(() => container.classList.add("theater-mode"));
          } else {
            container.classList.add("theater-mode");
          }
        } else if (document.fullscreenElement === container && document.exitFullscreen) {
          document.exitFullscreen().catch(() => container.classList.remove("theater-mode"));
        } else {
          container.classList.remove("theater-mode");
        }
        syncFullscreenButton(enabled);
        window.setTimeout(onResize, 80);
      }

      function applyStoryState(patch) {
        const labelPatch = patch?.labels;
        const settingsPatch = cloneSettings(patch || {});
        if (Object.prototype.hasOwnProperty.call(settingsPatch, "labels")) delete settingsPatch.labels;
        const preserveEpoch = !Object.prototype.hasOwnProperty.call(patch || {}, "epochYear");
        const preserveCamera = !(patch || {}).camera;
        mergeSettings(threeSettings, settingsPatch);
        applyStoryLabelsPatch(labelPatch);
        if (threeLightPreset && threeSettings.lightPreset) {
          threeLightPreset.value = threeSettings.lightPreset;
        }
        applyThreeSettings({ preserveEpoch, preserveCamera });
        syncDebugTextareaFromLive();
      }

      function runCaptionCue(cue) {
        const fadeIn = cue.fadeIn ?? 250;
        const fadeOut = cue.fadeOut ?? 350;
        const duration = cue.duration ?? 1200;
        const opts = { color: cue.color, sizeRem: cue.sizeRem };
        setStoryCaption(cue.text, false, 0, opts);
        activeStoryTimers.push(window.setTimeout(() => setStoryCaption(cue.text, true, fadeIn, opts), 20));
        activeStoryTimers.push(window.setTimeout(() => setStoryCaption(cue.text, false, fadeOut, opts), Math.max(20, duration - fadeOut)));
      }

      function runCameraCue(cue) {
        const cueCamera = cue.camera || cue.state?.camera;
        if (!camera || !controls || !cueCamera) return;
        const duration = cue.duration ?? 1000;
        const startTime = performance.now();
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const endPos = new THREE.Vector3(
          cueCamera.position?.x ?? camera.position.x,
          cueCamera.position?.y ?? camera.position.y,
          cueCamera.position?.z ?? camera.position.z
        );
        const endTarget = new THREE.Vector3(
          cueCamera.target?.x ?? controls.target.x,
          cueCamera.target?.y ?? controls.target.y,
          cueCamera.target?.z ?? controls.target.z
        );
        if (typeof cueCamera.fov === "number") {
          camera.fov = cueCamera.fov;
          camera.updateProjectionMatrix();
        }
        if (typeof cueCamera.minDistance === "number") controls.minDistance = cueCamera.minDistance;
        if (typeof cueCamera.maxDistance === "number") controls.maxDistance = cueCamera.maxDistance;
        const restoreOrbitMode = orbitMode;
        controls.minPolarAngle = 0;
        controls.maxPolarAngle = Math.PI;
        const tick = (now) => {
          const t = Math.min(1, (now - startTime) / duration);
          const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
          camera.position.lerpVectors(startPos, endPos, eased);
          controls.target.lerpVectors(startTarget, endTarget, eased);
          controls.update();
          if (t < 1 && activeStoryId) {
            activeStoryFrame = window.requestAnimationFrame(tick);
          } else {
            activeStoryFrame = null;
            threeSettings.camera.position = {
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            };
            threeSettings.camera.target = {
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            };
            applyOrbitMode(restoreOrbitMode);
            syncDebugTextareaFromLive();
          }
        };
        activeStoryFrame = window.requestAnimationFrame(tick);
      }

      function runEpochTravelCue(cue) {
        if (!window.explorerState || typeof window.explorerRender !== "function") return;
        const duration = cue.duration ?? 5000;
        const step = cue.step || data.meta.epoch_step || 100;
        const startYear = cue.from;
        const endYear = cue.to;
        const startTime = performance.now();
        let lastApplied = null;
        const tick = (now) => {
          const t = Math.min(1, (now - startTime) / duration);
          const rawYear = startYear + (endYear - startYear) * t;
          const steppedYear = Math.round(rawYear / step) * step;
          if (steppedYear !== lastApplied) {
            lastApplied = steppedYear;
            let bestIndex = 0;
            let bestDistance = Number.POSITIVE_INFINITY;
            data.epochs.forEach((epoch, index) => {
              const distance = Math.abs(epoch.year - steppedYear);
              if (distance < bestDistance) {
                bestDistance = distance;
                bestIndex = index;
              }
            });
            window.explorerState.epochIndex = bestIndex;
            window.explorerRender();
            threeSettings.epochYear = data.epochs[bestIndex].year;
            syncDebugTextareaFromLive();
          }
          if (t < 1 && activeStoryId) {
            activeStoryFrame = window.requestAnimationFrame(tick);
          } else {
            activeStoryFrame = null;
          }
        };
        activeStoryFrame = window.requestAnimationFrame(tick);
      }

      function runFlashCue(cue) {
        const descriptors = transitionDescriptorsForTarget(cue.target);
        if (!descriptors.length) return;
        const duration = cue.duration ?? 900;
        const steps = 12;
        const baseScales = new WeakMap();
        markTransitionObjects(descriptors, true);
        descriptors.forEach((entry) => {
          setTransitionEntryVisible(entry, true);
          entry.items.forEach((item) => {
            if (item.object.scale) baseScales.set(item.object, item.object.scale.clone());
          });
        });
        for (let step = 0; step <= steps; step += 1) {
          const delay = (duration * step) / steps;
          activeStoryTimers.push(window.setTimeout(() => {
            const wave = Math.sin((Math.PI * step) / steps);
            descriptors.forEach((entry) => {
              entry.items.forEach((item) => {
                setObjectOpacity(item.object, item.opacity + Math.max(0.25, item.opacity) * wave);
                if (item.object.scale) {
                  const baseScale = baseScales.get(item.object);
                  const scale = 1 + (item.flashScale ?? 0.18) * wave;
                  if (baseScale) item.object.scale.copy(baseScale).multiplyScalar(scale);
                }
              });
            });
            if (step === steps) {
              descriptors.forEach((entry) => {
                entry.items.forEach((item) => {
                  setObjectOpacity(item.object, item.opacity);
                  const baseScale = baseScales.get(item.object);
                  if (baseScale) item.object.scale.copy(baseScale);
                });
              });
              markTransitionObjects(descriptors, false);
              applyThreeSettings({ preserveEpoch: true, preserveCamera: true });
            }
          }, delay));
        }
      }

      const transitionDefaults = {
        eclipticGrid: { mode: "stagger", order: "default", duration: 1000 },
        referencePlanes: { mode: "fade", order: "default", duration: 700 },
        eclipticPlane: { mode: "fade", order: "default", duration: 700 },
        equatorialPlane: { mode: "fade", order: "default", duration: 700 },
        nsAxis: { mode: "fade", order: "default", duration: 700 },
        eclipticBand: { mode: "fade", order: "ecliptic", duration: 900 },
        eclipticDividers: { mode: "rollout", order: "ecliptic", duration: 1200 },
        eclipticLabels: { mode: "stagger", order: "ecliptic", duration: 1200 },
        eclipticPoles: { mode: "fade", order: "default", duration: 600 },
        eclipticNakSegments: { mode: "rollout", order: "ecliptic", duration: 1300 },
        stars: { mode: "fade", order: "default", duration: 900 },
        nakshatraStars: { mode: "rollout", order: "ecliptic", duration: 1200 },
        nakshatras: { mode: "rollout", order: "ecliptic", duration: 1800 },
        polarItems: { mode: "rollout", order: "default", duration: 1600 },
        northPolarItems: { mode: "rollout", order: "default", duration: 1200 },
        southPolarItems: { mode: "rollout", order: "default", duration: 1200 },
        poleTrack: { mode: "rollout", order: "default", duration: 1100 },
        precessionCircle: { mode: "fade", order: "default", duration: 900 },
        seasonalFrame: { mode: "rollout", order: "default", duration: 1300 },
        overlay: { mode: "fade", order: "default", duration: 500 },
        default: { mode: "fade", order: "default", duration: 800 },
      };

      function transitionPatchForTarget(target, visible) {
        const patches = {
          eclipticGrid: { ui: { showGrid: visible } },
          equatorialGrid: { ui: { showEquatorialGrid: visible } },
          referencePlanes: { ui: { showReferencePlanes: visible, showEclipticPlane: visible, showEquatorialPlane: visible } },
          eclipticPlane: { ui: { showReferencePlanes: true, showEclipticPlane: visible } },
          equatorialPlane: { ui: { showReferencePlanes: true, showEquatorialPlane: visible } },
          nsAxis: { ui: { showNsAxis: visible } },
          eclipticBand: { ui: { showEclipticBand: visible } },
          eclipticDividers: { ui: { showEclipticDividers: visible } },
          eclipticLabels: { ui: { showEclipticLabels: visible } },
          eclipticPoles: { ui: { showEclipticPoles: visible } },
          NEP: { ui: { showEclipticPoles: true, showNEP: visible } },
          SEP: { ui: { showEclipticPoles: true, showSEP: visible } },
          eclipticNakSegments: { ui: { showEclipticBand: visible, showEclipticDividers: visible, showEclipticLabels: visible, showEclipticPoles: visible } },
          stars: { ui: { showStars: visible } },
          nakshatraStars: { ui: { showNakshatraStars: visible } },
          nakshatras: { ui: { showNakshatraLines: visible, showNakshatraLabels: visible } },
          nakshatraLines: { ui: { showNakshatraLines: visible } },
          nakshatraLabels: { ui: { showNakshatraLabels: visible } },
          polarItems: { ui: { showPolarItems: visible } },
          northPolarItems: { ui: { showPolarItems: true, showNorthPolarItems: visible } },
          southPolarItems: { ui: { showPolarItems: true, showSouthPolarItems: visible } },
          poleTrack: { ui: { showPoleTrack: visible, showNP: visible, showSP: visible } },
          precessionCircle: { ui: { showPoleTrack: visible } },
          seasonalFrame: { ui: { showSeasonalFrame: visible } },
          equator: { ui: { showSeasonalFrame: true } },
          VE: { ui: { showSeasonalFrame: true } },
          SS: { ui: { showSeasonalFrame: true } },
          AE: { ui: { showSeasonalFrame: true } },
          WS: { ui: { showSeasonalFrame: true } },
          NP: { ui: { showPoleTrack: true, showNP: visible } },
          SP: { ui: { showPoleTrack: true, showSP: visible } },
          overlay: { ui: { showOverlay: visible } },
        };
        const polarMatches = polarMatchesForTarget(target);
        if (polarMatches.length) {
          const regions = new Set(polarMatches.map((entry) => entry.region));
          const patch = visible ? { ui: { showPolarItems: true } } : { ui: {} };
          if (visible && regions.has("north")) patch.ui.showNorthPolarItems = true;
          if (visible && regions.has("south")) patch.ui.showSouthPolarItems = true;
          return patch;
        }
        return patches[target] || null;
      }

      function setObjectOpacity(object, opacity) {
        if (!object?.material) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.forEach((material) => {
          material.transparent = true;
          material.opacity = Math.min(1, Math.max(0, opacity));
          material.needsUpdate = true;
        });
      }

      function transitionDescriptor(object, opacity = 1, order = 0) {
        return { items: [{ object, opacity }], order };
      }

      function transitionGroup(items, order = 0) {
        return { items, order };
      }

      function normalizeNakKey(value) {
        return String(value || "")
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .replace(/[^a-z0-9]/gi, "")
          .toLowerCase();
      }

      function specialTargetAliases(...values) {
        const aliases = new Set();
        values.forEach((value) => {
          const key = normalizeNakKey(value);
          if (key) aliases.add(key);
        });
        if (aliases.has("convedic25codexshim") || aliases.has("shimsumara") || aliases.has("simsumara")) {
          aliases.add("sisumara");
          aliases.add("shishumara");
          aliases.add("shimshumara");
        }
        if (aliases.has("convedic25codexmatsya")) aliases.add("matsya");
        if (aliases.has("agastya") || aliases.has("canopus") || aliases.has("hip30438")) {
          aliases.add("agastya");
          aliases.add("canopus");
        }
        if (aliases.has("thuban") || aliases.has("hip68756")) {
          aliases.add("thuban");
          aliases.add("abhayadhruva");
        }
        if (aliases.has("polaris") || aliases.has("hip11767")) {
          aliases.add("polaris");
          aliases.add("matsyadhruva");
        }
        return Array.from(aliases);
      }

      const nakAliasMap = new Map();
      const nakSectorAliasMap = new Map();
      data.nakshatras.forEach((row) => {
        const abbr = normalizeNakKey((row.nid || "").split("-").pop());
        const english = normalizeNakKey(row.enaks);
        const index = String(row.sector_index_27 || row.meta_index_28).padStart(2, "0");
        const sector = Number(row.sector_index_27 || row.meta_index_28);
        [abbr, english, `n${index}`].forEach((alias) => {
          if (alias) nakAliasMap.set(alias, row.nid);
          if (alias && Number.isFinite(sector)) nakSectorAliasMap.set(alias, sector);
        });
      });
      Object.entries({
        pph: "N11-PPhal", uph: "N12-UPhal", pas: "N20-PAsh", uas: "N21-UAsh",
        ppr: "N25-PPros", pbh: "N25-PPros", upr: "N26-UPros", ubh: "N26-UPros",
        abh: "N28-Abh", n28: "N28-Abh",
      }).forEach(([alias, nid]) => nakAliasMap.set(alias, nid));

      function resolveNakAlias(queryRaw) {
        const query = normalizeNakKey(queryRaw);
        if (nakAliasMap.has(query)) return { nid: nakAliasMap.get(query) };
        const matches = Array.from(nakAliasMap.entries()).filter(([alias]) => alias.startsWith(query));
        if (matches.length === 1) return { nid: matches[0][1] };
        return null;
      }

      function sectorForNakNid(nid) {
        const row = data.nakshatras.find((item) => item.nid === nid);
        const sector = Number(row?.sector_index_27 || row?.meta_index_28);
        return Number.isFinite(sector) ? sector : null;
      }

      function resolveSectorQuery(queryRaw) {
        const raw = String(queryRaw || "");
        const numeric = Number(raw);
        if (Number.isInteger(numeric)) return numeric;
        const resolved = resolveNakAlias(raw);
        return resolved ? sectorForNakNid(resolved.nid) : null;
      }

      function resolveNakshatraTarget(target) {
        const raw = String(target || "");
        if (!/^[$*@]/.test(raw)) return null;
        const sigil = raw[0];
        const resolved = resolveNakAlias(raw.slice(1));
        return resolved ? { sigil, nid: resolved.nid } : null;
      }

      function resolvePreciseTarget(target) {
        const match = String(target || "").match(/^(nak|sector)\.([\w-]+)(?:\.(stars|lines|label))?$/i);
        if (!match) return null;
        const family = match[1].toLowerCase();
        const query = match[2];
        const part = (match[3] || (family === "nak" ? "all" : "")).toLowerCase();
        if (family === "nak") {
          const resolved = resolveNakAlias(query);
          return resolved ? { family, nid: resolved.nid, part } : null;
        }
        if (family === "sector") {
          const sector = resolveSectorQuery(query);
          return Number.isFinite(sector) ? { family, sector, part: part || "label" } : null;
        }
        return null;
      }

      function setTransitionEntryVisible(entry, visible) {
        entry.items.forEach((item) => { item.object.visible = visible; });
      }

      function setTransitionEntryOpacity(entry, progress) {
        entry.items.forEach((item) => setObjectOpacity(item.object, item.opacity * progress));
      }

      function markTransitionObjects(descriptors, active) {
        descriptors.forEach((entry) => {
          entry.items.forEach((item) => {
            if (active) activeTransitionObjects.add(item.object);
            else activeTransitionObjects.delete(item.object);
          });
        });
      }

      function targetVisible(target) {
        return targetVisibilityOverrides.get(target) !== false;
      }

      function targetStyle(target, part) {
        return threeSettings.targetStyles?.[target]?.[part] || {};
      }

      function registerRuntimeStyleTarget(target) {
        if (target) runtimePreciseStyleRegistry.add(target);
      }

      function firstDefined(...values) {
        return values.find((value) => value !== undefined && value !== null);
      }

      function setMeshStyle(mesh, style, fallbackColor = null, fallbackOpacity = null, fallbackSize = null) {
        if (!mesh) return;
        if (!mesh.userData.baseScale) mesh.userData.baseScale = mesh.scale.clone();
        if (mesh.material) {
          const color = firstDefined(style.color, fallbackColor);
          const opacity = firstDefined(style.alpha, fallbackOpacity);
          if (color && mesh.material.color) mesh.material.color.set(color);
          if (opacity !== undefined) {
            mesh.material.transparent = true;
            mesh.material.opacity = opacity;
          }
        }
        const size = firstDefined(style.size, fallbackSize);
        if (size !== undefined && Number.isFinite(Number(size))) {
          mesh.scale.copy(mesh.userData.baseScale).multiplyScalar(Number(size));
        }
      }

      function setLineStyle(line, style, fallbackColor = null, fallbackOpacity = null) {
        if (!line?.material) return;
        const color = firstDefined(style.color, fallbackColor);
        const opacity = firstDefined(style.alpha, fallbackOpacity);
        if (color && line.material.color) line.material.color.set(color);
        if (opacity !== undefined) {
          line.material.transparent = true;
          line.material.opacity = opacity;
        }
        if (style.width !== undefined) line.material.linewidth = Number(style.width) || 1;
      }

      function setSpriteStyle(sprite, style, fallbackOpacity = null, fallbackSize = null, fallbackColor = null) {
        if (!sprite) return;
        const color = firstDefined(style.color, fallbackColor);
        const opacity = firstDefined(style.alpha, fallbackOpacity);
        const size = firstDefined(style.size, fallbackSize);
        if (color) setSpriteTextColor(sprite, color);
        if (opacity !== undefined && sprite.material) sprite.material.opacity = opacity;
        if (size !== undefined) setSpriteHeight(sprite, Number(size));
      }

      function styleTargetsForPolarEntry(entry) {
        const out = [];
        (entry.aliases || []).forEach((alias) => {
          const key = normalizeNakKey(alias);
          const canonical = {
            agastya: "agastya",
            canopus: "agastya",
            thuban: "thuban",
            abhayadhruva: "thuban",
            polaris: "polaris",
            matsyadhruva: "polaris",
            matsya: "matsya",
            sisumara: "sisumara",
            shishumara: "sisumara",
            shimshumara: "sisumara",
          }[key] || alias;
          if (!out.includes(canonical)) out.push(canonical);
        });
        return out;
      }

      function polarEntryStyle(entry) {
        const part = entry.kind === "label" ? "label" : entry.kind === "dot" ? "dot" : "line";
        const merged = {};
        styleTargetsForPolarEntry(entry).forEach((target) => Object.assign(merged, targetStyle(target, part)));
        return merged;
      }

      function isSeasonalLeafTarget(target) {
        return ["equator", "VE", "SS", "AE", "WS"].includes(target);
      }

      function seasonalTargetVisible(target) {
        if (focusedSeasonalTargets.size && !focusedSeasonalTargets.has(target)) return false;
        return targetVisible(target);
      }

      function setFocusedSeasonalTarget(target, visible) {
        if (visible && isSeasonalLeafTarget(target)) focusedSeasonalTargets.add(target);
      }

      function clearFocusedSeasonalTarget(target) {
        if (target === "seasonalFrame") focusedSeasonalTargets.clear();
      }

      function focusedPolarVisible(entry) {
        const focused = focusedPolarTargets[entry.region];
        if (!focused || focused.size === 0) return true;
        return (entry.aliases || []).some((alias) => focused.has(alias));
      }

      function polarMatchesForTarget(target) {
        return polarItemRefs.filter((entry) => (entry.aliases || []).includes(target));
      }

      function setFocusedPolarTarget(target, visible) {
        polarMatchesForTarget(target).forEach((entry) => {
          const focused = focusedPolarTargets[entry.region];
          (entry.aliases || []).forEach((alias) => {
            if (visible) focused.add(alias);
            else focused.delete(alias);
          });
        });
      }

      function clearFocusedPolarTarget(target) {
        if (target === "northPolarItems" || target === "polarItems") focusedPolarTargets.north.clear();
        if (target === "southPolarItems" || target === "polarItems") focusedPolarTargets.south.clear();
      }

      function aliasesVisible(aliases = []) {
        return aliases.every((alias) => targetVisible(alias));
      }

      function polarOpacity(entry) {
        return entry.kind === "line"
          ? threeSettings.polarItems.opacity
          : entry.kind === "dot"
            ? threeSettings.polarItems.starOpacity
            : threeSettings.polarItems.labelOpacity;
      }

      function transitionDescriptorsForTarget(target) {
        const preciseTarget = resolvePreciseTarget(target);
        if (preciseTarget) {
          const items = [];
          if (preciseTarget.family === "nak") {
            if (preciseTarget.part === "all" || preciseTarget.part === "lines") {
              nakshatraLineRefs.filter((entry) => entry.nid === preciseTarget.nid).forEach((entry) => {
                registerRuntimeStyleTarget(`nak.${preciseTarget.nid}.lines`);
                Object.assign(targetStyle(`nak.${preciseTarget.nid}.lines`, "line"), targetStyle(target, "line"));
                items.push({ object: entry.line, opacity: threeSettings.nakshatras.selectedOpacity });
              });
            }
            if (preciseTarget.part === "all" || preciseTarget.part === "stars") {
              starGroupRefs.filter((entry) => entry.nid === preciseTarget.nid).forEach((entry) => {
                registerRuntimeStyleTarget(`nak.${preciseTarget.nid}.stars`);
                Object.assign(targetStyle(`nak.${preciseTarget.nid}.stars`, "dot"), targetStyle(target, "dot"));
                items.push({ object: entry.points, opacity: threeSettings.stars.opacity });
              });
            }
            if (preciseTarget.part === "all" || preciseTarget.part === "label") {
              nakshatraLabelRefs.filter((entry) => entry.nid === preciseTarget.nid).forEach((entry) => {
                registerRuntimeStyleTarget(`nak.${preciseTarget.nid}.label`);
                Object.assign(targetStyle(`nak.${preciseTarget.nid}.label`, "label"), targetStyle(target, "label"));
                items.push({ object: entry.sprite, opacity: 1, flashScale: 0.45 });
              });
            }
          } else if (preciseTarget.family === "sector") {
            if (preciseTarget.part && preciseTarget.part !== "label") return [];
            bandRefs.labels.filter((entry) => entry.userData?.sectorIndex === preciseTarget.sector).forEach((label) => {
              registerRuntimeStyleTarget(`sector.${preciseTarget.sector}.label`);
              Object.assign(targetStyle(`sector.${preciseTarget.sector}.label`, "label"), targetStyle(target, "label"));
              items.push({ object: label, opacity: 1, flashScale: 0.45 });
            });
          }
          return items.length ? [transitionGroup(items, 0)] : [];
        }
        const nakTarget = resolveNakshatraTarget(target);
        if (nakTarget) {
          const items = [];
          if (nakTarget.sigil === "$" || nakTarget.sigil === "@") {
            nakshatraLineRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {
              items.push({ object: entry.line, opacity: threeSettings.nakshatras.selectedOpacity });
            });
          }
          if (nakTarget.sigil === "*" || nakTarget.sigil === "@") {
            starGroupRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {
              items.push({ object: entry.points, opacity: threeSettings.stars.opacity });
            });
          }
          return items.length ? [transitionGroup(items, 0)] : [];
        }
        if (target === "eclipticGrid") {
          return [
            ...gridRefs.parallels.map((line, index) => transitionDescriptor(line, threeSettings.grid.parallelOpacity, index)),
            ...gridRefs.meridians.map((line, index) => transitionDescriptor(line, threeSettings.grid.meridianOpacity, index + gridRefs.parallels.length)),
          ];
        }
        if (target === "equatorialGrid") {
          return [
            ...gridRefs.equatorialParallels.map((line, index) => transitionDescriptor(line, threeSettings.grid.equatorialOpacity, index)),
            ...gridRefs.equatorialMeridians.map((line, index) => transitionDescriptor(line, threeSettings.grid.equatorialOpacity, index + gridRefs.equatorialParallels.length)),
          ];
        }
        if (target === "referencePlanes") {
          return [
            ...(eclipticPlane ? [transitionDescriptor(eclipticPlane, threeSettings.reference.eclipticPlaneOpacity, 0)] : []),
            ...(equatorialPlane ? [transitionDescriptor(equatorialPlane, threeSettings.reference.equatorialPlaneOpacity, 1)] : []),
          ];
        }
        if (target === "eclipticPlane") {
          return eclipticPlane ? [transitionDescriptor(eclipticPlane, threeSettings.reference.eclipticPlaneOpacity, 0)] : [];
        }
        if (target === "equatorialPlane") {
          return equatorialPlane ? [transitionDescriptor(equatorialPlane, threeSettings.reference.equatorialPlaneOpacity, 0)] : [];
        }
        if (target === "nsAxis") {
          return nsAxisLine ? [transitionDescriptor(nsAxisLine, threeSettings.reference.nsAxisOpacity, 0)] : [];
        }
        if (target === "eclipticBand") {
          return [
            ...bandRefs.meshes.map((mesh, index) => transitionDescriptor(mesh, threeSettings.ecliptic.bandOpacity, index)),
            ...(eclipticCircle ? [transitionDescriptor(eclipticCircle, threeSettings.ecliptic.circleOpacity, bandRefs.meshes.length)] : []),
          ];
        }
        if (target === "eclipticDividers") {
          return bandRefs.dividers.map((line, index) => transitionDescriptor(line, threeSettings.ecliptic.dividerOpacity, index));
        }
        if (target === "eclipticLabels") {
          return bandRefs.labels.map((label, index) => transitionDescriptor(label, threeSettings.ecliptic.sectorLabelOpacity, index));
        }
        if (target === "eclipticPoles") {
          return [
            ...eclipticPoleDots.map((dot, index) => transitionDescriptor(dot, 1, index)),
            ...eclipticPoleLabels.map((label, index) => transitionDescriptor(label, threeSettings.ecliptic.poleLabelOpacity, index + eclipticPoleDots.length)),
          ];
        }
        if (target === "NEP" || target === "SEP") {
          return eclipticPoleRefs
            .filter((entry) => entry.key === target)
            .map((entry, index) => transitionDescriptor(entry.object, entry.kind === "label" ? threeSettings.ecliptic.poleLabelOpacity : 1, index));
        }
        if (target === "eclipticNakSegments") {
          return [
            ...transitionDescriptorsForTarget("eclipticBand"),
            ...transitionDescriptorsForTarget("eclipticDividers"),
            ...transitionDescriptorsForTarget("eclipticLabels"),
            ...transitionDescriptorsForTarget("eclipticPoles"),
          ];
        }
        if (target === "stars") {
          return starGroupRefs
            .map((entry) => transitionDescriptor(entry.points, threeSettings.stars.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }
        if (target === "nakshatraStars") {
          return starGroupRefs
            .filter((entry) => entry.nid !== "__special__")
            .map((entry) => transitionDescriptor(entry.points, threeSettings.stars.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }
        if (target === "nakshatraLines") {
          return nakshatraLineRefs
            .map((entry) => transitionDescriptor(entry.line, threeSettings.nakshatras.opacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }
        if (target === "nakshatraLabels") {
          return nakshatraLabelRefs
            .map((entry) => transitionDescriptor(entry.sprite, threeSettings.nakshatras.labelOpacity, entry.metaIndex ?? 0))
            .sort((a, b) => a.order - b.order);
        }
        if (target === "nakshatras") {
          const grouped = new Map();
          nakshatraLineRefs.forEach((entry) => {
            const orderKey = entry.metaIndex ?? 0;
            if (!grouped.has(orderKey)) grouped.set(orderKey, []);
            grouped.get(orderKey).push({ object: entry.line, opacity: threeSettings.nakshatras.opacity });
          });
          nakshatraLabelRefs.forEach((entry) => {
            const orderKey = entry.metaIndex ?? 0;
            if (!grouped.has(orderKey)) grouped.set(orderKey, []);
            grouped.get(orderKey).push({ object: entry.sprite, opacity: threeSettings.nakshatras.labelOpacity });
          });
          return Array.from(grouped.entries())
            .sort(([a], [b]) => a - b)
            .map(([orderKey, items]) => transitionGroup(items, orderKey));
        }
        if (target === "polarItems") {
          return polarItemRefs.map((entry, index) => {
            return transitionDescriptor(entry.object, polarOpacity(entry), index);
          });
        }
        if (target === "northPolarItems" || target === "southPolarItems") {
          const region = target === "northPolarItems" ? "north" : "south";
          return polarItemRefs.filter((entry) => entry.region === region).map((entry, index) => {
            return transitionDescriptor(entry.object, polarOpacity(entry), index);
          });
        }
        const polarMatches = polarItemRefs.filter((entry) => (entry.aliases || []).includes(target));
        if (polarMatches.length) {
          return polarMatches.map((entry, index) => transitionDescriptor(entry.object, polarOpacity(entry), index));
        }
        if (target === "poleTrack") {
          return [
            ...(poleTrackCircle ? [transitionDescriptor(poleTrackCircle, threeSettings.poleTrack.opacity, 0)] : []),
            ...(poleTrackArc ? [transitionDescriptor(poleTrackArc, threeSettings.poleTrack.arcOpacity, 1)] : []),
            ...(poleTrackLabel ? [transitionDescriptor(poleTrackLabel, threeSettings.poleTrack.trackLabelOpacity, 2)] : []),
            ...(poleDot ? [transitionDescriptor(poleDot, 1, 3)] : []),
            ...(movingPoleLabel ? [transitionDescriptor(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 4)] : []),
            ...(southPoleDot ? [transitionDescriptor(southPoleDot, 1, 5)] : []),
            ...(southPoleLabel ? [transitionDescriptor(southPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 6)] : []),
          ];
        }
        if (target === "precessionCircle") {
          return poleTrackCircle ? [transitionDescriptor(poleTrackCircle, threeSettings.poleTrack.opacity, 0)] : [];
        }
        if (target === "seasonalFrame") {
          return [
            ...(equatorLine ? [transitionDescriptor(equatorLine, threeSettings.seasonal.equatorOpacity, 0)] : []),
            ...seasonalMarkerRefs.flatMap((entry, index) => [
              transitionDescriptor(entry.mesh, 1, index + 1),
              transitionDescriptor(entry.sprite, threeSettings.seasonal.markerLabelOpacity, index + 1.1),
            ]),
          ];
        }
        if (target === "equator") {
          return equatorLine ? [transitionDescriptor(equatorLine, threeSettings.seasonal.equatorOpacity, 0)] : [];
        }
        if (["VE", "SS", "AE", "WS"].includes(target)) {
          return seasonalMarkerRefs
            .filter((entry) => entry.key === target)
            .flatMap((entry) => [
              transitionDescriptor(entry.mesh, 1, 0),
              transitionDescriptor(entry.sprite, threeSettings.seasonal.markerLabelOpacity, 1),
            ]);
        }
        if (target === "NP") {
          return [
            ...(poleDot ? [transitionDescriptor(poleDot, 1, 0)] : []),
            ...(movingPoleLabel ? [transitionDescriptor(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 1)] : []),
          ];
        }
        if (target === "SP") {
          return [
            ...(southPoleDot ? [transitionDescriptor(southPoleDot, 1, 0)] : []),
            ...(southPoleLabel ? [transitionDescriptor(southPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 1)] : []),
          ];
        }
        return [];
      }

      function setOverlayTransition(visible, progress) {
        if (!overlayLabel?.parentElement) return;
        overlayLabel.parentElement.style.display = visible || progress > 0 ? "" : "none";
        overlayLabel.parentElement.style.opacity = String((threeSettings.overlay.opacity ?? 1) * progress);
      }

      function finalizeTransition(target, visible, descriptors = null, hasPatch = false) {
        activeTransitionTargets.delete(target);
        if (descriptors) markTransitionObjects(descriptors, false);
        if (polarMatchesForTarget(target).length) setFocusedPolarTarget(target, visible);
        clearFocusedPolarTarget(target);
        setFocusedSeasonalTarget(target, visible);
        clearFocusedSeasonalTarget(target);
        targetVisibilityOverrides.set(target, visible);
        const patch = transitionPatchForTarget(target, visible);
        if (patch) mergeSettings(threeSettings, patch);
        applyThreeSettings({ preserveEpoch: true, preserveCamera: true });
        syncDebugTextareaFromLive();
      }

      function runTransitionCue(cue, visible) {
        const target = cue.target;
        const patch = transitionPatchForTarget(target, visible);
        const defaults = transitionDefaults[target] || transitionDefaults.default;
        const mode = cue.mode || defaults.mode;
        const duration = Number(cue.duration ?? defaults.duration);
        const order = cue.order || defaults.order;
        const direction = cue.direction || (visible ? "forward" : "reverse");
        if (visible && polarMatchesForTarget(target).length) setFocusedPolarTarget(target, true);
        if (visible) clearFocusedPolarTarget(target);
        if (visible) setFocusedSeasonalTarget(target, true);
        if (visible) clearFocusedSeasonalTarget(target);
        activeTransitionTargets.add(target);

        if (target === "overlay") {
          mergeSettings(threeSettings, patch);
          const steps = mode === "instant" ? 1 : 12;
          for (let step = 0; step <= steps; step += 1) {
            const delay = steps === 1 ? 0 : (duration * step) / steps;
            activeStoryTimers.push(window.setTimeout(() => {
              const t = steps === 1 ? 1 : step / steps;
              setOverlayTransition(visible, visible ? t : 1 - t);
              if (step === steps) finalizeTransition(target, visible);
            }, delay));
          }
          return;
        }

        let descriptors = transitionDescriptorsForTarget(target);
        if (!patch && descriptors.length === 0) {
          activeTransitionTargets.delete(target);
          return;
        }
        if (direction === "reverse" || order === "reverse-ecliptic") descriptors = descriptors.slice().reverse();
        if (mode === "instant" || descriptors.length === 0) {
          finalizeTransition(target, visible);
          return;
        }
        markTransitionObjects(descriptors, true);

        if (visible) {
          if (patch) mergeSettings(threeSettings, patch);
          applyThreeSettings({ preserveEpoch: true, preserveCamera: true });
          descriptors.forEach((entry) => {
            setTransitionEntryVisible(entry, false);
            setTransitionEntryOpacity(entry, 0);
          });
        }

        if (mode === "fade") {
          const steps = 12;
          descriptors.forEach((entry) => setTransitionEntryVisible(entry, true));
          for (let step = 0; step <= steps; step += 1) {
            const delay = (duration * step) / steps;
            activeStoryTimers.push(window.setTimeout(() => {
              const t = step / steps;
              descriptors.forEach((entry) => {
                const progress = visible ? t : 1 - t;
                setTransitionEntryVisible(entry, progress > 0);
                setTransitionEntryOpacity(entry, progress);
              });
              if (step === steps) finalizeTransition(target, visible, descriptors);
            }, delay));
          }
          return;
        }

        const staggerSpan = Math.max(0, duration * 0.85);
        const denominator = Math.max(1, descriptors.length - 1);
        descriptors.forEach((entry, index) => {
          const delay = (staggerSpan * index) / denominator;
          activeStoryTimers.push(window.setTimeout(() => {
            setTransitionEntryVisible(entry, visible);
            setTransitionEntryOpacity(entry, visible ? 1 : 0);
          }, delay));
        });
        activeStoryTimers.push(window.setTimeout(() => finalizeTransition(target, visible, descriptors), duration));
      }

      function resolveCueTime(token, previousEnd) {
        if (typeof token === "number") return Math.max(0, token);
        if (typeof token === "string") {
          const trimmed = token.trim();
          const value = Number(trimmed);
          if (!Number.isFinite(value)) {
            throw new Error(`Invalid cue time: ${token}`);
          }
          return /^[+-]/.test(trimmed) ? Math.max(0, previousEnd + value) : Math.max(0, value);
        }
        return previousEnd;
      }

      function cueDurationForScheduling(cue) {
        if (Object.prototype.hasOwnProperty.call(cue, "duration")) {
          const duration = Number(cue.duration);
          return Number.isFinite(duration) ? duration : 0;
        }
        if (cue.action === "caption") return 1200;
        if (cue.action === "camera") return 1000;
        if (cue.action === "epochTravel") return 5000;
        if (cue.action === "flash") return 900;
        if (cue.action === "reveal" || cue.action === "hide") {
          const defaults = transitionDefaults[cue.target] || transitionDefaults.default;
          return defaults.duration || 0;
        }
        return 0;
      }

      function normalizeStoryCues(story) {
        const source = story?.cues || [];
        const rawCues = Array.isArray(source)
          ? source
          : Object.entries(source).map(([at, cue]) => ({ ...(cue || {}), at }));
        let previousEnd = 0;
        return rawCues.map((cue) => {
          const token = Object.prototype.hasOwnProperty.call(cue, "at")
            ? cue.at
            : Object.prototype.hasOwnProperty.call(cue, "after")
              ? `+${cue.after}`
              : "+0";
          const scheduledAt = resolveCueTime(token, previousEnd);
          const duration = cueDurationForScheduling(cue);
          previousEnd = Math.max(previousEnd, scheduledAt + Math.max(0, duration));
          return { ...cue, _scheduledAt: scheduledAt };
        });
      }

      function runStory(story) {
        if (!story) return;
        if (!scene) initThree();
        stopStory();
        activeStoryId = story.id;
        if (storyStrip) {
          storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {
            button.classList.toggle("active", button.dataset.storyId === story.id);
          });
        }
        if (story.initial) {
          applyStoryState(cloneSettings(story.initial));
        }
        normalizeStoryCues(story).forEach((cue) => {
          const timer = window.setTimeout(() => {
            if (activeStoryId !== story.id) return;
            if (cue.action === "caption") runCaptionCue(cue);
            if (cue.action === "set") applyStoryState(cue.state);
            if (cue.action === "reveal") runTransitionCue(cue, true);
            if (cue.action === "hide") runTransitionCue(cue, false);
            if (cue.action === "camera") runCameraCue(cue);
            if (cue.action === "epochTravel") runEpochTravelCue(cue);
            if (cue.action === "flash") runFlashCue(cue);
            if (cue.action === "fullscreen") setThreeFullscreen(true);
            if (cue.action === "exitFullscreen") setThreeFullscreen(false);
          }, cue._scheduledAt);
          activeStoryTimers.push(timer);
        });
      }

      function storySearchText(story) {
        return [
          story.id,
          story.title,
          story.group,
          ...(Array.isArray(story.tags) ? story.tags : []),
        ].filter(Boolean).join(" ").toLowerCase();
      }

      function filteredStories() {
        const query = (threeStorySearch?.value || "").trim().toLowerCase();
        const sorted = stories.slice().sort((a, b) => {
          const ao = Number.isFinite(Number(a.order)) ? Number(a.order) : 9999;
          const bo = Number.isFinite(Number(b.order)) ? Number(b.order) : 9999;
          return ao - bo || String(a.title).localeCompare(String(b.title));
        });
        if (!query) return sorted;
        return sorted.filter((story) => storySearchText(story).includes(query));
      }

      function storyById(id) {
        return stories.find((story) => story.id === id) || null;
      }

      function renderStoryPills() {
        if (!storyStrip) return;
        const featured = filteredStories().filter((story) => story.featured).slice(0, 5);
        storyStrip.innerHTML = featured.map((story) => `
          <button class="three-story-pill" type="button" data-story-id="${story.id}">${story.title}</button>
        `).join("");
        storyStrip.querySelectorAll(".three-story-pill").forEach((button) => {
          button.addEventListener("click", () => {
            const story = stories.find((item) => item.id === button.dataset.storyId);
            if (story && threeStorySelect) threeStorySelect.value = story.id;
            loadStoryIntoEditors(story);
            runStory(story);
          });
        });
      }

      function storyVysuSource(story) {
        return story?.vysu || defaultVyomaSutra;
      }

      function loadStoryIntoEditors(story) {
        if (!story) return;
        if (threeStoryEditor) threeStoryEditor.value = JSON.stringify(story, null, 2);
        if (threeVysuEditor) threeVysuEditor.value = storyVysuSource(story);
        syncVysuLineNumbers();
      }

      function renderStoryEditorOptions() {
        if (!threeStorySelect || !threeStoryEditor) return;
        const options = filteredStories();
        const previousValue = threeStorySelect.value;
        threeStorySelect.innerHTML = options.map((story) => `
          <option value="${story.id}">${story.title}</option>
        `).join("");
        const selected = options.find((story) => story.id === previousValue) || options[0] || null;
        if (selected) {
          threeStorySelect.value = selected.id;
          loadStoryIntoEditors(selected);
          const shown = options.length === stories.length ? `${stories.length} story source(s).` : `${options.length} of ${stories.length} story source(s).`;
          setStoryStatus(shown);
        } else {
          threeStoryEditor.value = "";
          if (threeVysuEditor && !threeVysuEditor.value.trim()) threeVysuEditor.value = defaultVyomaSutra;
          syncVysuLineNumbers();
          setStoryStatus("No build-time stories found.");
        }
      }

      function selectedStoryOriginal() {
        if (!threeStorySelect) return stories[0] || null;
        return stories.find((story) => story.id === threeStorySelect.value) || stories[0] || null;
      }

      function storyCueList(story) {
        const source = story?.cues || [];
        return Array.isArray(source)
          ? source.map((cue, index) => [index, cue])
          : Object.entries(source).map(([at, cue]) => [at, { ...(cue || {}), at }]);
      }

      function validateStoryForEditor(story) {
        const validActions = new Set(["caption", "set", "reveal", "hide", "camera", "epochTravel", "flash", "fullscreen", "exitFullscreen"]);
        storyCueList(story).forEach(([index, cue]) => {
          if (!cue || typeof cue !== "object" || Array.isArray(cue)) {
            throw new Error(`Cue ${index} must be an object.`);
          }
          if (!cue.action) {
            throw new Error(`Cue ${index} is missing action. Camera cues need "action": "camera".`);
          }
          if (!validActions.has(cue.action)) {
            throw new Error(`Cue ${index} has unknown action "${cue.action}".`);
          }
          if (cue.action === "caption" && !Object.prototype.hasOwnProperty.call(cue, "text")) {
            throw new Error(`Cue ${index} caption needs text.`);
          }
          if (cue.action === "set" && !cue.state) {
            throw new Error(`Cue ${index} set needs state.`);
          }
          if ((cue.action === "reveal" || cue.action === "hide") && !cue.target) {
            throw new Error(`Cue ${index} ${cue.action} needs target.`);
          }
          if (cue.action === "flash" && !cue.target) {
            throw new Error(`Cue ${index} flash needs target.`);
          }
          if (cue.action === "camera" && !cue.camera && !cue.state?.camera) {
            throw new Error(`Cue ${index} camera needs camera.`);
          }
          if (cue.action === "epochTravel") {
            ["from", "to", "duration"].forEach((key) => {
              if (!Object.prototype.hasOwnProperty.call(cue, key)) {
                throw new Error(`Cue ${index} epochTravel needs ${key}.`);
              }
            });
          }
        });
      }

      function storyFromEditor() {
        if (!threeStoryEditor) return null;
        const parsed = JSON.parse(threeStoryEditor.value);
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
          throw new Error("Story JSON must be an object.");
        }
        if (!parsed.id || !parsed.title || (!Array.isArray(parsed.cues) && (!parsed.cues || typeof parsed.cues !== "object"))) {
          throw new Error("Story needs id, title, and cues.");
        }
        validateStoryForEditor(parsed);
        return parsed;
      }

      function setDockTab(tabName) {
        threeDockTabs.forEach((button) => {
          button.classList.toggle("active", button.dataset.dockTab === tabName);
        });
        Object.entries(threeDockPanels).forEach(([name, panel]) => {
          if (panel) panel.classList.toggle("active", name === tabName);
        });
      }

      function captureThreeSettings() {
        if (!camera || !controls) return cloneSettings(threeSettings);
        return {
          ...cloneSettings(threeSettings),
          epochYear: data.epochs[window.explorerState?.epochIndex ?? 0]?.year ?? threeSettings.epochYear,
          camera: {
            ...cloneSettings(threeSettings).camera,
            position: {
              x: Number(camera.position.x.toFixed(3)),
              y: Number(camera.position.y.toFixed(3)),
              z: Number(camera.position.z.toFixed(3)),
            },
            target: {
              x: Number(controls.target.x.toFixed(3)),
              y: Number(controls.target.y.toFixed(3)),
              z: Number(controls.target.z.toFixed(3)),
            },
            fov: Number(camera.fov.toFixed(3)),
            minDistance: Number(controls.minDistance.toFixed(3)),
            maxDistance: Number(controls.maxDistance.toFixed(3)),
          },
        };
      }

      function syncDebugTextareaFromLive() {
        if (threeDebugJson) {
          threeDebugJson.value = JSON.stringify(captureThreeSettings(), null, 2);
        }
      }

      function renderThreeDebugToggles() {
        if (!threeDebugToggles) return;
        threeDebugToggles.innerHTML = threeDebugUiFields
          .map(([key, label]) => `
            <label class="three-debug-flag">
              <input type="checkbox" data-ui-flag="${key}">
              <span>${label}</span>
            </label>
          `)
          .join("");
        threeDebugToggles.querySelectorAll("input[data-ui-flag]").forEach((input) => {
          input.addEventListener("change", () => {
            const key = input.getAttribute("data-ui-flag");
            threeSettings.ui[key] = input.checked;
            applyThreeSettings({ preserveEpoch: true, preserveCamera: true });
            syncDebugTextareaFromLive();
            setDebugStatus(`${input.checked ? "Show" : "Hide"}: ${key}`);
          });
        });
      }

      function syncThreeDebugTogglesFromSettings() {
        if (!threeDebugToggles) return;
        threeDebugUiFields.forEach(([key]) => {
          const input = threeDebugToggles.querySelector(`input[data-ui-flag="${key}"]`);
          if (input) input.checked = threeSettings.ui[key] !== false;
        });
      }

      function applyLightPreset() {
        if (!scene) return;
        const preset = threeSettings.lightPreset || "night";
        const background = preset === "day" ? 0xdfe8f2 : preset === "twilight" ? 0x1b2436 : 0x080810;
        scene.background = new THREE.Color(background);
      }

      function applyThreeSettings(options = {}) {
        if (!scene || !camera || !controls) return;
        const preserveEpoch = options.preserveEpoch === true;
        const preserveCamera = options.preserveCamera === true;
        if (!preserveEpoch && typeof threeSettings.epochYear === "number" && window.explorerState && typeof window.explorerRender === "function") {
          let bestIndex = 0;
          let bestDistance = Number.POSITIVE_INFINITY;
          data.epochs.forEach((epoch, index) => {
            const distance = Math.abs(epoch.year - threeSettings.epochYear);
            if (distance < bestDistance) {
              bestDistance = distance;
              bestIndex = index;
            }
          });
          window.explorerState.epochIndex = bestIndex;
          window.explorerRender();
        }
        if (!preserveCamera) {
          camera.fov = threeSettings.camera.fov;
          camera.position.set(
            threeSettings.camera.position.x,
            threeSettings.camera.position.y,
            threeSettings.camera.position.z
          );
          camera.updateProjectionMatrix();
          controls.target.set(
            threeSettings.camera.target.x,
            threeSettings.camera.target.y,
            threeSettings.camera.target.z
          );
          controls.minDistance = threeSettings.camera.minDistance;
          controls.maxDistance = threeSettings.camera.maxDistance;
        }
        applyOrbitMode();
        applyLightPreset();
        if (siderealGroup && builtEclipticGridStep !== gridStep(threeSettings.grid.eclipticStepDeg)) {
          buildSphereGrid();
        }
        if (seasonalGroup && builtEquatorialGridStep !== gridStep(threeSettings.grid.equatorialStepDeg)) {
          buildEquatorialGrid();
        }

        gridRefs.parallels.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          setLineStyle(line, targetStyle("eclipticGrid", "line"), threeSettings.grid.parallelColor, threeSettings.grid.parallelOpacity);
        });
        gridRefs.meridians.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          setLineStyle(line, targetStyle("eclipticGrid", "line"), threeSettings.grid.meridianColor, threeSettings.grid.meridianOpacity);
        });
        gridRefs.equatorialParallels.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          setLineStyle(line, targetStyle("equatorialGrid", "line"), threeSettings.grid.equatorialColor, threeSettings.grid.equatorialOpacity);
        });
        gridRefs.equatorialMeridians.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          setLineStyle(line, targetStyle("equatorialGrid", "line"), threeSettings.grid.equatorialColor, threeSettings.grid.equatorialOpacity);
        });

        if (eclipticPlane) {
          eclipticPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEclipticPlane !== false;
          setMeshStyle(eclipticPlane, targetStyle("eclipticPlane", "fill"), threeSettings.reference.eclipticPlaneColor, threeSettings.reference.eclipticPlaneOpacity);
        }
        if (equatorialPlane) {
          equatorialPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEquatorialPlane !== false;
          setMeshStyle(equatorialPlane, targetStyle("equatorialPlane", "fill"), threeSettings.reference.equatorialPlaneColor, threeSettings.reference.equatorialPlaneOpacity);
        }
        if (nsAxisLine) {
          nsAxisLine.visible = threeSettings.ui.showNsAxis;
          setLineStyle(nsAxisLine, targetStyle("nsAxis", "line"), threeSettings.reference.nsAxisColor, threeSettings.reference.nsAxisOpacity);
        }

        bandRefs.meshes.forEach((mesh) => {
          if (activeTransitionObjects.has(mesh)) return;
          mesh.visible = threeSettings.ui.showEclipticBand;
          setMeshStyle(mesh, targetStyle("eclipticBand", "fill"), null, threeSettings.ecliptic.bandOpacity);
        });
        bandRefs.dividers.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.visible = threeSettings.ui.showEclipticDividers;
          setLineStyle(line, targetStyle("eclipticDividers", "line"), threeSettings.ecliptic.circleColor, threeSettings.ecliptic.dividerOpacity);
        });
        bandRefs.labels.forEach((label) => {
          if (activeTransitionObjects.has(label)) return;
          label.visible = threeSettings.ui.showEclipticLabels;
          const style = { ...targetStyle("eclipticLabels", "label"), ...targetStyle(`sector.${label.userData?.sectorIndex}.label`, "label") };
          setSpriteStyle(label, style, threeSettings.ecliptic.sectorLabelOpacity, threeSettings.ecliptic.sectorLabelSize);
        });
        eclipticPoleLabels.forEach((label) => {
          if (activeTransitionObjects.has(label)) return;
          const isSep = label.name === "SEP";
          const style = targetStyle(isSep ? "SEP" : "NEP", "label");
          label.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
          setSpriteStyle(label, style, threeSettings.ecliptic.poleLabelOpacity, threeSettings.ecliptic.poleLabelSize);
        });
        eclipticPoleDots.forEach((dot) => {
          if (activeTransitionObjects.has(dot)) return;
          const isSep = dot.name === "SEP";
          dot.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
          setMeshStyle(dot, targetStyle(isSep ? "SEP" : "NEP", "dot"));
        });
        if (eclipticCircle) {
          if (!activeTransitionObjects.has(eclipticCircle)) {
            eclipticCircle.visible = threeSettings.ui.showEclipticBand;
            setLineStyle(eclipticCircle, targetStyle("eclipticBand", "line"), threeSettings.ecliptic.circleColor, threeSettings.ecliptic.circleOpacity);
          }
        }

        starGroupRefs.forEach((entry) => {
          if (activeTransitionObjects.has(entry.points)) return;
          entry.points.visible = threeSettings.ui.showStars;
          const style = targetStyle(entry.nid === "__special__" ? "stars" : "nakshatraStars", "dot");
          entry.points.material.size = firstDefined(style.size, threeSettings.stars.size);
          entry.points.material.opacity = firstDefined(style.alpha, threeSettings.stars.opacity);
        });

        if (poleTrackCircle) {
          poleTrackCircle.visible = threeSettings.ui.showPoleTrack;
          setLineStyle(poleTrackCircle, targetStyle("precessionCircle", "line"), threeSettings.poleTrack.color, threeSettings.poleTrack.opacity);
        }
        if (poleTrackArc) {
          poleTrackArc.visible = threeSettings.ui.showPoleTrack;
          poleTrackArc.material.color.set(threeSettings.poleTrack.arcColor);
          poleTrackArc.material.opacity = threeSettings.poleTrack.arcOpacity;
        }
        if (poleTrackLabel) {
          poleTrackLabel.visible = threeSettings.ui.showPoleTrack;
          setSpriteStyle(poleTrackLabel, targetStyle("precessionCircle", "label"), threeSettings.poleTrack.trackLabelOpacity, threeSettings.poleTrack.trackLabelSize);
        }
        if (poleDot) {
          poleDot.visible = threeSettings.ui.showPoleTrack && threeSettings.ui.showNP !== false;
          setMeshStyle(poleDot, targetStyle("NP", "dot"), threeSettings.poleTrack.dotColor);
        }
        if (movingPoleLabel) {
          movingPoleLabel.visible = threeSettings.ui.showPoleTrack && threeSettings.ui.showNP !== false;
          setSpriteStyle(movingPoleLabel, targetStyle("NP", "label"), threeSettings.poleTrack.movingPoleLabelOpacity, threeSettings.poleTrack.movingPoleLabelSize);
        }
        if (southPoleDot) {
          southPoleDot.visible = threeSettings.ui.showPoleTrack && threeSettings.ui.showSP !== false;
          setMeshStyle(southPoleDot, targetStyle("SP", "dot"), threeSettings.poleTrack.dotColor);
        }
        if (southPoleLabel) {
          southPoleLabel.visible = threeSettings.ui.showPoleTrack && threeSettings.ui.showSP !== false;
          setSpriteStyle(southPoleLabel, targetStyle("SP", "label"), threeSettings.poleTrack.movingPoleLabelOpacity * 0.72, threeSettings.poleTrack.movingPoleLabelSize * 0.9);
        }
        if (equatorLine) {
          equatorLine.visible = threeSettings.ui.showSeasonalFrame && seasonalTargetVisible("equator");
          setLineStyle(equatorLine, targetStyle("equator", "line"), threeSettings.seasonal.equatorColor, threeSettings.seasonal.equatorOpacity);
        }
        seasonalMarkerRefs.forEach((entry) => {
          const markerVisible = threeSettings.ui.showSeasonalFrame && seasonalTargetVisible(entry.key);
          entry.mesh.visible = markerVisible;
          entry.sprite.visible = markerVisible;
          setMeshStyle(entry.mesh, targetStyle(entry.key, "dot"), null, null, threeSettings.seasonal.markerScale);
          setSpriteStyle(entry.sprite, targetStyle(entry.key, "label"), threeSettings.seasonal.markerLabelOpacity, threeSettings.seasonal.markerLabelSize * threeSettings.seasonal.markerScale);
        });

        gridRefs.parallels.forEach((line) => { if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showGrid; });
        gridRefs.meridians.forEach((line) => { if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showGrid; });
        gridRefs.equatorialParallels.forEach((line) => { if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showEquatorialGrid; });
        gridRefs.equatorialMeridians.forEach((line) => { if (!activeTransitionObjects.has(line)) line.visible = threeSettings.ui.showEquatorialGrid; });
        if (overlayLabel) {
          overlayLabel.parentElement.style.display = threeSettings.ui.showOverlay ? "" : "none";
          overlayLabel.parentElement.style.fontSize = `${threeSettings.overlay.fontSizeRem}rem`;
          overlayLabel.parentElement.style.opacity = String(threeSettings.overlay.opacity);
        }

        syncThreeDebugTogglesFromSettings();
        updateThreeState();
      }

      function updateThreeState() {
        if (!window.explorerState) return;
        const st = window.explorerState;
        const transitioningNakshatras = activeTransitionTargets.has("nakshatras");
        if (!transitioningNakshatras && !activeTransitionTargets.has("nakshatraLines")) {
          nakshatraLineRefs.forEach((entry) => {
            if (activeTransitionObjects.has(entry.line)) return;
            const active = entry.metaIndex === st.selectedMetaIndex;
            const visible = threeSettings.ui.showNakshatraLines && st.visibleNakshatras[entry.nid] !== false;
            const style = { ...targetStyle("nakshatraLines", "line"), ...targetStyle(`nak.${entry.nid}.lines`, "line") };
            entry.line.visible = visible;
            setLineStyle(entry.line, style, active ? threeSettings.nakshatras.selectedColor : threeSettings.nakshatras.color, visible ? (active ? threeSettings.nakshatras.selectedOpacity : threeSettings.nakshatras.opacity) : 0);
          });
        }
        if (!transitioningNakshatras && !activeTransitionTargets.has("nakshatraLabels")) {
          nakshatraLabelRefs.forEach((entry) => {
            if (activeTransitionObjects.has(entry.sprite)) return;
            const visible = threeSettings.ui.showNakshatraLabels && st.visibleNakshatras[entry.nid] !== false;
            entry.sprite.visible = visible;
            const style = { ...targetStyle("nakshatraLabels", "label"), ...targetStyle(`nak.${entry.nid}.label`, "label") };
            setSpriteStyle(entry.sprite, style, visible ? threeSettings.nakshatras.labelOpacity : 0, threeSettings.nakshatras.labelSize);
          });
        }
        if (!activeTransitionTargets.has("stars") && !activeTransitionTargets.has("nakshatraStars")) {
          starGroupRefs.forEach((entry) => {
            if (activeTransitionObjects.has(entry.points)) return;
            const visible = entry.nid === "__special__"
              ? threeSettings.ui.showStars
              : (threeSettings.ui.showStars || threeSettings.ui.showNakshatraStars) && st.visibleNakshatras[entry.nid] !== false;
            const style = entry.nid === "__special__" ? targetStyle("stars", "dot") : { ...targetStyle("nakshatraStars", "dot"), ...targetStyle(`nak.${entry.nid}.stars`, "dot") };
            entry.points.visible = visible;
            entry.points.material.opacity = visible ? firstDefined(style.alpha, threeSettings.stars.opacity) : 0;
            entry.points.material.size = firstDefined(style.size, threeSettings.stars.size);
          });
        }
        polarItemRefs.forEach((entry) => {
          const regionVisible = entry.region === "south"
            ? threeSettings.ui.showSouthPolarItems !== false
            : threeSettings.ui.showNorthPolarItems !== false;
          const visible = threeSettings.ui.showPolarItems && regionVisible && focusedPolarVisible(entry) && aliasesVisible(entry.aliases) && st.visibleCodex[entry.id] !== false;
          const style = polarEntryStyle(entry);
          entry.object.visible = visible;
          if (entry.object.material) {
            if (entry.kind === "line") setLineStyle(entry.object, style, threeSettings.polarItems.color, threeSettings.polarItems.opacity);
            if (entry.kind === "dot") setMeshStyle(entry.object, style, threeSettings.polarItems.color, threeSettings.polarItems.starOpacity);
            if (entry.kind === "label") {
              setSpriteStyle(entry.object, style, threeSettings.polarItems.labelOpacity, threeSettings.polarItems.labelSize);
            }
          }
        });
        syncLayerButtons();
      }

      /* ── init ────────────────────────────────────────────── */
      function initThree() {
        scene = new THREE.Scene();
        applyLightPreset();

        camera = new THREE.PerspectiveCamera(
          threeSettings.camera.fov, container.clientWidth / container.clientHeight, 1, 2000
        );
        camera.position.set(
          threeSettings.camera.position.x,
          threeSettings.camera.position.y,
          threeSettings.camera.position.z
        );

        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;
        controls.target.set(
          threeSettings.camera.target.x,
          threeSettings.camera.target.y,
          threeSettings.camera.target.z
        );
        controls.minDistance = threeSettings.camera.minDistance;
        controls.maxDistance = threeSettings.camera.maxDistance;
        controls.enablePan = false;
        applyOrbitMode();

        siderealGroup = new THREE.Group();
        scene.add(siderealGroup);
        seasonalGroup = new THREE.Group();
        scene.add(seasonalGroup);

        buildSphereGrid();
        buildEquatorialGrid();
        buildReferencePrimitives();
        buildEclipticBand();
        buildEclipticCircle();
        buildStars();
        buildNakshatraLines();
        buildNakshatraLabels();
        buildCodexFigures();
        buildSpecialStars();
        buildPoleTrack();
        buildSeasonalFrame();
        applyThreeSettings();
        syncDebugTextareaFromLive();

        window.addEventListener('resize', onResize);
        animate();
      }

      /* ── A1. Sphere wireframe ───────────────────────────── */
      function buildSphereGrid() {
        removeObjects(gridRefs.parallels, siderealGroup);
        removeObjects(gridRefs.meridians, siderealGroup);
        const parMat = new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.grid.parallelColor), transparent: true, opacity: threeSettings.grid.parallelOpacity });
        const merMat = new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.grid.meridianColor), transparent: true, opacity: threeSettings.grid.meridianOpacity });
        const step = gridStep(threeSettings.grid.eclipticStepDeg);
        builtEclipticGridStep = step;
        for (let lat = -90 + step; lat < 90; lat += step) {
          if (lat === 0) continue;
          const g = new THREE.BufferGeometry().setFromPoints(circlePoints(lat, R * 0.995, 72));
          const line = new THREE.Line(g, parMat.clone());
          gridRefs.parallels.push(line);
          siderealGroup.add(line);
        }
        for (let lon = 0; lon < 360; lon += step) {
          const g = new THREE.BufferGeometry().setFromPoints(meridianPoints(lon, R * 0.995, 72));
          const line = new THREE.Line(g, merMat.clone());
          gridRefs.meridians.push(line);
          siderealGroup.add(line);
        }
        if (eclipticPoleDots.length > 0) return;
        // ecliptic poles
        const poleMat = new THREE.MeshBasicMaterial({ color: 0x8899aa });
        const poleGeom = new THREE.SphereGeometry(1.2, 8, 8);
        const nep = new THREE.Mesh(poleGeom, poleMat);
        nep.name = 'NEP';
        nep.position.copy(toCart(0, 90, R * 0.995));
        eclipticPoleDots.push(nep);
        eclipticPoleRefs.push({ key: 'NEP', kind: 'dot', object: nep });
        siderealGroup.add(nep);
        const sep = new THREE.Mesh(poleGeom.clone(), poleMat);
        sep.name = 'SEP';
        sep.position.copy(toCart(0, -90, R * 0.995));
        eclipticPoleDots.push(sep);
        eclipticPoleRefs.push({ key: 'SEP', kind: 'dot', object: sep });
        siderealGroup.add(sep);
        const nepLabel = makeTextSprite('NEP', { color: '#8899aa', fontSize: 36, size: 7.0, opacity: 0.6 });
        nepLabel.name = 'NEP';
        nepLabel.position.copy(toCart(15, 85, R * 1.04));
        eclipticPoleLabels.push(nepLabel);
        eclipticPoleRefs.push({ key: 'NEP', kind: 'label', object: nepLabel });
        siderealGroup.add(nepLabel);
        const sepLabel = makeTextSprite('SEP', { color: '#8899aa', fontSize: 36, size: 7.0, opacity: 0.6 });
        sepLabel.name = 'SEP';
        sepLabel.position.copy(toCart(15, -85, R * 1.04));
        eclipticPoleLabels.push(sepLabel);
        eclipticPoleRefs.push({ key: 'SEP', kind: 'label', object: sepLabel });
        siderealGroup.add(sepLabel);
      }

      function buildEquatorialGrid() {
        removeObjects(gridRefs.equatorialParallels, seasonalGroup);
        removeObjects(gridRefs.equatorialMeridians, seasonalGroup);
        const mat = new THREE.LineBasicMaterial({
          color: new THREE.Color(threeSettings.grid.equatorialColor),
          transparent: true,
          opacity: threeSettings.grid.equatorialOpacity,
        });
        const step = gridStep(threeSettings.grid.equatorialStepDeg);
        builtEquatorialGridStep = step;
        for (let dec = -90 + step; dec < 90; dec += step) {
          if (dec === 0) continue;
          const line = new THREE.Line(new THREE.BufferGeometry(), mat.clone());
          line.userData.gridKind = "parallel";
          line.userData.decDeg = dec;
          gridRefs.equatorialParallels.push(line);
          seasonalGroup.add(line);
        }
        for (let ra = 0; ra < 360; ra += step) {
          const line = new THREE.Line(new THREE.BufferGeometry(), mat.clone());
          line.userData.gridKind = "meridian";
          line.userData.raDeg = ra;
          gridRefs.equatorialMeridians.push(line);
          seasonalGroup.add(line);
        }
      }

      function buildDiscFromRing(points) {
        const positions = [0, 0, 0];
        points.forEach((point) => positions.push(point.x, point.y, point.z));
        const indices = [];
        for (let i = 1; i < points.length; i += 1) indices.push(0, i, i + 1);
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geom.setIndex(indices);
        geom.computeVertexNormals();
        return geom;
      }

      function buildReferencePrimitives() {
        const eclipticGeom = buildDiscFromRing(circlePoints(0, R * 0.985, 144).slice(0, -1));
        eclipticPlane = new THREE.Mesh(eclipticGeom, new THREE.MeshBasicMaterial({
          color: new THREE.Color(threeSettings.reference.eclipticPlaneColor),
          transparent: true,
          opacity: threeSettings.reference.eclipticPlaneOpacity,
          side: THREE.DoubleSide,
          depthWrite: false,
        }));
        siderealGroup.add(eclipticPlane);

        equatorialPlane = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshBasicMaterial({
          color: new THREE.Color(threeSettings.reference.equatorialPlaneColor),
          transparent: true,
          opacity: threeSettings.reference.equatorialPlaneOpacity,
          side: THREE.DoubleSide,
          depthWrite: false,
        }));
        seasonalGroup.add(equatorialPlane);

        nsAxisLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({
          color: new THREE.Color(threeSettings.reference.nsAxisColor),
          transparent: true,
          opacity: threeSettings.reference.nsAxisOpacity,
          depthWrite: false,
        }));
        seasonalGroup.add(nsAxisLine);
      }

      /* ── A2. Ecliptic band — colored + labeled sectors ─── */
      function buildEclipticBand() {
        const sectorRows = data.nakshatras.filter(n => n.sector_index_27 !== null);
        const step = 2;

        sectorRows.forEach((row, idx) => {
          const lonStart = row.sector_start_lon_deg;
          const lonEnd   = row.sector_end_lon_deg;
          const span = ((lonEnd - lonStart) % 360 + 360) % 360 || (360 / 27);
          const nSteps = Math.max(2, Math.round(span / step));
          const color = sectorHex(idx);

          const positions = [];
          const indices   = [];
          for (let i = 0; i <= nSteps; i++) {
            const lon = lonStart + (i / nSteps) * span;
            const pTop = toCart(lon,  BAND_HALF, R * 0.998);
            const pBot = toCart(lon, -BAND_HALF, R * 0.998);
            positions.push(pTop.x, pTop.y, pTop.z);
            positions.push(pBot.x, pBot.y, pBot.z);
            if (i < nSteps) {
              const b = i * 2;
              indices.push(b, b + 1, b + 2, b + 1, b + 3, b + 2);
            }
          }
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setIndex(indices);
          geom.computeVertexNormals();
          const mat = new THREE.MeshBasicMaterial({
            color: color, transparent: true, opacity: threeSettings.ecliptic.bandOpacity,
            side: THREE.DoubleSide, depthWrite: false
          });
          const mesh = new THREE.Mesh(geom, mat);
          bandRefs.meshes.push(mesh);
          siderealGroup.add(mesh);

          const divPts = [];
          for (let lat = -BAND_HALF; lat <= BAND_HALF; lat += 1) {
            divPts.push(toCart(lonStart, lat, R * 0.999));
          }
          const divGeom = new THREE.BufferGeometry().setFromPoints(divPts);
          const divMat = new THREE.LineBasicMaterial({ color: 0xd4a56a, transparent: true, opacity: threeSettings.ecliptic.dividerOpacity });
          const divider = new THREE.Line(divGeom, divMat);
          bandRefs.dividers.push(divider);
          siderealGroup.add(divider);

          const midLon = lonStart + span / 2;
          const abbr = row.nid.split('-')[1] || '';
          const label = makeTextSprite(abbr, {
            color: sectorHSL(idx), fontSize: 36, size: 7.5, opacity: 0.82, bold: true
          });
          label.position.copy(toCart(midLon, 0, R * 1.025));
          label.userData.sectorIndex = row.sector_index_27;
          label.userData.nid = row.nid;
          bandRefs.labels.push(label);
          siderealGroup.add(label);
        });
      }

      /* ── Ecliptic great circle ──────────────────────────── */
      function buildEclipticCircle() {
        const pts = circlePoints(0, R * 1.001, 144);
        const geom = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.ecliptic.circleColor), transparent: true, opacity: threeSettings.ecliptic.circleOpacity });
        eclipticCircle = new THREE.Line(geom, mat);
        siderealGroup.add(eclipticCircle);
      }

      /* ── Stars ──────────────────────────────────────────── */
      function buildStars() {
        data.nakshatras.forEach(naks => {
          if (!naks.stars || naks.stars.length === 0) return;
          const positions = [];
          const colors = [];
          naks.stars.forEach(star => {
            const p = toCart(star.lon_deg, star.lat_deg, R);
            positions.push(p.x, p.y, p.z);
            colors.push(0.92, 0.92, 1.0);
          });
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
          const mat = new THREE.PointsMaterial({
            size: threeSettings.stars.size, vertexColors: true, transparent: true, opacity: threeSettings.stars.opacity, sizeAttenuation: true
          });
          const points = new THREE.Points(geom, mat);
          starGroupRefs.push({ nid: naks.nid, metaIndex: naks.meta_index_28, points });
          siderealGroup.add(points);
        });
        if (data.special_stars.length > 0) {
          const positions = [];
          const colors = [];
          data.special_stars.forEach(star => {
            const p = toCart(star.lon_deg, star.lat_deg, R);
            positions.push(p.x, p.y, p.z);
            colors.push(0.78, 0.86, 1.0);
          });
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
          const mat = new THREE.PointsMaterial({
            size: threeSettings.stars.size * 1.15, vertexColors: true, transparent: true, opacity: threeSettings.stars.opacity, sizeAttenuation: true
          });
          const points = new THREE.Points(geom, mat);
          starGroupRefs.push({ nid: "__special__", metaIndex: 99, points });
          siderealGroup.add(points);
        }
      }

      /* ── Nakshatra asterism lines ───────────────────────── */
      function buildNakshatraLines() {
        data.nakshatras.forEach(naks => {
          naks.asterism_lines.forEach(line => {
            const pts = [];
            line.forEach(hip => {
              const star = data.stars.find(s => s.hip === hip);
              if (star) pts.push(toCart(star.lon_deg, star.lat_deg, R * 0.999));
            });
            if (pts.length > 1) {
              const geom = new THREE.BufferGeometry().setFromPoints(pts);
              const lineObj = new THREE.Line(geom, new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.nakshatras.color), transparent: true, opacity: threeSettings.nakshatras.opacity }));
              nakshatraLineRefs.push({ nid: naks.nid, metaIndex: naks.meta_index_28, line: lineObj });
              siderealGroup.add(lineObj);
            }
          });
        });
      }

      /* ── Nakshatra labels ───────────────────────────────── */
      function buildNakshatraLabels() {
        data.nakshatras.forEach(naks => {
          if (!naks.stars || naks.stars.length === 0) return;
          const cLon = naks.stars.reduce((s, st) => s + st.lon_deg, 0) / naks.stars.length;
          const cLat = naks.stars.reduce((s, st) => s + st.lat_deg, 0) / naks.stars.length;
          const label = makeTextSprite(naks.enaks, {
            color: '#99aabb', fontSize: 32, size: 6.5, opacity: threeSettings.nakshatras.labelOpacity
          });
          label.position.copy(toCart(cLon, cLat + 3, R * 1.03));
          nakshatraLabelRefs.push({ nid: naks.nid, metaIndex: naks.meta_index_28, sprite: label });
          siderealGroup.add(label);
        });
      }

      /* ── Polar figures ────────────────────────────────────── */
      function buildCodexFigures() {
        const figMat = new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.opacity });
        const figDotMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.starOpacity });
        const figDotGeom = new THREE.SphereGeometry(0.7, 6, 6);

        const specialStarLookup = {};
        data.special_figures.forEach(fig => {
          fig.stars.forEach(s => { specialStarLookup[s.hip] = s; });
        });
        data.special_stars.forEach(s => { specialStarLookup[s.hip] = s; });

        data.special_figures.forEach(fig => {
          const avgLat = fig.stars.reduce((a, s) => a + s.lat_deg, 0) / Math.max(1, fig.stars.length);
          const region = avgLat < 0 ? "south" : "north";
          const figAliases = specialTargetAliases(fig.id, fig.label);
          fig.lines.forEach(line => {
            const pts = [];
            line.forEach(hip => {
              const s = specialStarLookup[hip];
              if (s) pts.push(toCart(s.lon_deg, s.lat_deg, R * 1.002));
            });
            if (pts.length > 1) {
              const geom = new THREE.BufferGeometry().setFromPoints(pts);
              const lineObj = new THREE.Line(geom, figMat.clone());
              polarItemRefs.push({ id: fig.id, region, kind: "line", object: lineObj, aliases: figAliases });
              siderealGroup.add(lineObj);
            }
          });
          fig.stars.forEach(s => {
            const dot = new THREE.Mesh(figDotGeom.clone(), figDotMat);
            dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.002));
            polarItemRefs.push({ id: fig.id, region, kind: "dot", object: dot, aliases: figAliases });
            siderealGroup.add(dot);
          });
          const cLon = fig.stars.reduce((a, s) => a + s.lon_deg, 0) / fig.stars.length;
          const cLat = fig.stars.reduce((a, s) => a + s.lat_deg, 0) / fig.stars.length;
          const figName = fig.id.includes('Shim') ? 'Śiśumāra' : fig.id.includes('Matsya') ? 'Matsya' : fig.label;
          const label = makeTextSprite(figName, {
            color: '#7a94b0', fontSize: 34, size: 8.5, opacity: threeSettings.polarItems.labelOpacity
          });
          label.position.copy(toCart(cLon, cLat + (fig.id.includes('Shim') ? 3 : -3), R * 1.04));
          polarItemRefs.push({ id: fig.id, region, kind: "label", object: label, aliases: figAliases });
          siderealGroup.add(label);
        });
      }

      /* ── Special stars (Agastya, Polaris, Thuban) ──────── */
      function buildSpecialStars() {
        const dotGeom = new THREE.SphereGeometry(1.0, 8, 8);
        const dotMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(threeSettings.polarItems.color), transparent: true, opacity: threeSettings.polarItems.starOpacity });

        data.special_stars.forEach(s => {
          const region = s.lat_deg < 0 ? "south" : "north";
          const aliases = specialTargetAliases(s.hip, s.label);
          const dot = new THREE.Mesh(dotGeom.clone(), dotMat);
          dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.002));
          polarItemRefs.push({ id: s.hip, region, kind: "dot", object: dot, aliases });
          siderealGroup.add(dot);
          const label = makeTextSprite(s.label, {
            color: '#7a94b0', fontSize: 30, size: 7.0, opacity: threeSettings.polarItems.labelOpacity
          });
          label.position.copy(toCart(s.lon_deg + 3, s.lat_deg - 3, R * 1.04));
          polarItemRefs.push({ id: s.hip, region, kind: "label", object: label, aliases });
          siderealGroup.add(label);
        });

        const specialStarLookup = {};
        data.special_figures.forEach(fig => {
          fig.stars.forEach(s => { specialStarLookup[s.hip] = s; });
        });

        const poleStarDefs = [
          { hip: 'HIP 11767', label: 'Polaris', color: '#5577aa' },
          { hip: 'HIP 68756', label: 'Thuban', color: '#5577aa' }
        ];
        poleStarDefs.forEach(def => {
          const s = specialStarLookup[def.hip] || data.stars.find(st => st.hip === def.hip);
          if (!s) return;
          const aliases = specialTargetAliases(def.hip, def.label);
          const psMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(def.color) });
          const dot = new THREE.Mesh(dotGeom.clone(), psMat);
          dot.position.copy(toCart(s.lon_deg, s.lat_deg, R * 1.003));
          polarItemRefs.push({ id: def.hip, region: "north", kind: "dot", object: dot, aliases });
          siderealGroup.add(dot);
          const label = makeTextSprite(def.label, {
            color: def.color, fontSize: 28, size: 6.5, opacity: 0.6
          });
          label.position.copy(toCart(s.lon_deg + 4, s.lat_deg - 3, R * 1.04));
          polarItemRefs.push({ id: def.hip, region: "north", kind: "label", object: label, aliases });
          siderealGroup.add(label);
        });
      }

      /* ── Precession circle ────────────────────────────────── */
      function buildPoleTrack() {
        // Full geometric precession circle: small circle at ecliptic lat = 90° − mean obliquity
        const meanObliquity = data.epochs[Math.floor(data.epochs.length / 2)].obliquity_deg || 23.44;
        const precLat = 90 - meanObliquity;
        const fullCirclePts = circlePoints(precLat, R * 1.005, 144);
        const fullGeom = new THREE.BufferGeometry().setFromPoints(fullCirclePts);
        const fullMat = new THREE.LineBasicMaterial({
          color: new THREE.Color(threeSettings.poleTrack.color),
          transparent: true,
          opacity: threeSettings.poleTrack.opacity,
          depthTest: false,
          depthWrite: false,
        });
        poleTrackCircle = new THREE.Line(fullGeom, fullMat);
        poleTrackCircle.renderOrder = 22;
        siderealGroup.add(poleTrackCircle);

        // Epoch-sampled arc overlay (brighter, shows covered range)
        const arcPts = data.epochs.map(e => toCart(e.north_pole_lon_deg, e.north_pole_lat_deg, R * 1.006));
        const arcGeom = new THREE.BufferGeometry().setFromPoints(arcPts);
        const arcMat = new THREE.LineBasicMaterial({
          color: new THREE.Color(threeSettings.poleTrack.arcColor),
          transparent: true,
          opacity: threeSettings.poleTrack.arcOpacity,
          depthTest: false,
          depthWrite: false,
        });
        poleTrackArc = new THREE.Line(arcGeom, arcMat);
        poleTrackArc.renderOrder = 23;
        siderealGroup.add(poleTrackArc);

        // Label
        const labelPos = toCart(180, precLat + 4, R * 1.05);
        poleTrackLabel = makeTextSprite('Precession Circle', {
          color: '#8899bb', fontSize: 30, size: 8.5, opacity: 0.6
        });
        poleTrackLabel.position.copy(labelPos);
        siderealGroup.add(poleTrackLabel);

        // Moving pole dot
        const poleGeom = new THREE.SphereGeometry(1.5, 10, 10);
        const poleMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(threeSettings.poleTrack.dotColor) });
        poleDot = new THREE.Mesh(poleGeom, poleMat);
        seasonalGroup.add(poleDot);
        southPoleDot = new THREE.Mesh(poleGeom.clone(), poleMat.clone());
        seasonalGroup.add(southPoleDot);

        const poleLabel = makeTextSprite('North Pole', {
          color: '#44566c', fontSize: 28, size: 7.0, opacity: 0.7
        });
        poleLabel.name = 'poleLabel';
        movingPoleLabel = poleLabel;
        seasonalGroup.add(poleLabel);
        southPoleLabel = makeTextSprite('South Pole', {
          color: '#44566c', fontSize: 26, size: 6.0, opacity: 0.48
        });
        southPoleLabel.name = 'southPoleLabel';
        seasonalGroup.add(southPoleLabel);
      }

      /* ── Seasonal frame (red equator + 4 markers) ──────── */
      function buildSeasonalFrame() {
        const eqGeom = new THREE.BufferGeometry();
        const eqMat = new THREE.LineBasicMaterial({ color: new THREE.Color(threeSettings.seasonal.equatorColor), transparent: true, opacity: threeSettings.seasonal.equatorOpacity });
        equatorLine = new THREE.Line(eqGeom, eqMat);
        seasonalGroup.add(equatorLine);

        equinoxMarkers = new THREE.Group();
        seasonalGroup.add(equinoxMarkers);
        const labels = ['VE', 'SS', 'AE', 'WS'];
        const mColors = [0xcc3333, 0xcc8833, 0xcc3333, 0x3388cc];
        labels.forEach((lbl, i) => {
          const mg = new THREE.SphereGeometry(1.5, 12, 12);
          const mm = new THREE.MeshBasicMaterial({ color: mColors[i] });
          const mesh = new THREE.Mesh(mg, mm);
          mesh.name = lbl;
          equinoxMarkers.add(mesh);
          const sprite = makeTextSprite(lbl, {
            color: '#' + mColors[i].toString(16).padStart(6, '0'),
            fontSize: 36, size: 8.5, opacity: 0.8, bold: true
          });
          sprite.name = lbl + '_label';
          seasonalMarkerRefs.push({ key: lbl, mesh, sprite, baseScale: sprite.scale.clone() });
          equinoxMarkers.add(sprite);
        });
      }

      /* ── update drifting frame ──────────────────────────── */
      function updateSeasonalFrame() {
        const st = window.explorerState;
        if (!st) return;
        const epoch = data.epochs[st.epochIndex];
        const flowText = timeFlow.direction > 0 ? ` · ${timeFlow.speed}x forward` : timeFlow.direction < 0 ? ` · ${timeFlow.speed}x backward` : "";
        overlayLabel.textContent = `${epoch.label}${flowText}`;
        syncTimeControls();
        const xAxis = toCart(epoch.vernal_equinox_lon_deg, 0, 1).normalize();
        const zAxis = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, 1).normalize();
        const yAxis = new THREE.Vector3().crossVectors(zAxis, xAxis).normalize();
        const equatorialPoint = (raDeg, decDeg, radius) => {
          const ra = raDeg * Math.PI / 180;
          const dec = decDeg * Math.PI / 180;
          return new THREE.Vector3()
            .addScaledVector(xAxis, Math.cos(dec) * Math.cos(ra))
            .addScaledVector(yAxis, Math.cos(dec) * Math.sin(ra))
            .addScaledVector(zAxis, Math.sin(dec))
            .normalize()
            .multiplyScalar(radius);
        };
        const updateEquatorialLine = (line) => {
          const pts = [];
          if (line.userData.gridKind === "parallel") {
            for (let ra = 0; ra <= 360; ra += 3) pts.push(equatorialPoint(ra, line.userData.decDeg, R * 0.993));
          } else {
            for (let dec = -90; dec <= 90; dec += 3) pts.push(equatorialPoint(line.userData.raDeg, dec, R * 0.993));
          }
          line.geometry.dispose();
          line.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        };
        gridRefs.equatorialParallels.forEach(updateEquatorialLine);
        gridRefs.equatorialMeridians.forEach(updateEquatorialLine);

        const pts = [];
        for (let lon = 0; lon <= 360; lon += 2) {
          const rel = (lon - epoch.vernal_equinox_lon_deg) * Math.PI / 180;
          const lat = Math.atan(
            -Math.tan(epoch.obliquity_deg * Math.PI / 180) * Math.sin(rel)
          ) * 180 / Math.PI;
          pts.push(toCart(lon, lat, R * 1.002));
        }
        equatorLine.geometry.dispose();
        equatorLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        if (equatorialPlane) {
          equatorialPlane.geometry.dispose();
          equatorialPlane.geometry = buildDiscFromRing(pts.slice(0, -1).map((point) => point.clone().multiplyScalar(0.985 / 1.002)));
        }

        const cardinals = [
          epoch.vernal_equinox_lon_deg,
          epoch.summer_solstice_lon_deg,
          epoch.autumnal_equinox_lon_deg,
          epoch.winter_solstice_lon_deg
        ];
        const labels = ['VE', 'SS', 'AE', 'WS'];
        cardinals.forEach((lonDeg, i) => {
          const p = toCart(lonDeg, 0, R * 1.006);
          const mesh = equinoxMarkers.getObjectByName(labels[i]);
          if (mesh) mesh.position.copy(p);
          const sprite = equinoxMarkers.getObjectByName(labels[i] + '_label');
          if (sprite) sprite.position.copy(toCart(lonDeg, 4, R * 1.04));
        });

        if (poleDot) {
          const pp = toCart(epoch.north_pole_lon_deg, epoch.north_pole_lat_deg, R * 1.006);
          poleDot.position.copy(pp);
          const poleLabel = seasonalGroup.getObjectByName('poleLabel');
          if (poleLabel) poleLabel.position.copy(toCart(epoch.north_pole_lon_deg + 5, epoch.north_pole_lat_deg - 3, R * 1.04));
          const sp = toCart(epoch.north_pole_lon_deg + 180, -epoch.north_pole_lat_deg, R * 1.006);
          if (southPoleDot) southPoleDot.position.copy(sp);
          if (southPoleLabel) southPoleLabel.position.copy(toCart(epoch.north_pole_lon_deg + 185, -epoch.north_pole_lat_deg + 3, R * 1.04));
          if (nsAxisLine) {
            nsAxisLine.geometry.dispose();
            nsAxisLine.geometry = new THREE.BufferGeometry().setFromPoints([sp, pp]);
          }
        }
      }

      /* ── resize / animate ──────────────────────────────── */
      function onResize() {
        if (!renderer) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }

      function animate() {
        requestAnimationFrame(animate);
        controls.update();
        updateThreeState();
        updateSeasonalFrame();
        updateStoryLabels();
        renderer.render(scene, camera);
      }

      function applyThreeSettingsFromTextarea() {
        if (!threeDebugJson) return;
        try {
          const parsed = JSON.parse(threeDebugJson.value);
          threeSettings = parsed;
          if (threeLightPreset && threeSettings.lightPreset) {
            threeLightPreset.value = threeSettings.lightPreset;
          }
          applyThreeSettings();
          syncDebugTextareaFromLive();
          setDebugStatus("Applied.");
        } catch (error) {
          setDebugStatus(`Invalid JSON: ${error.message}`);
        }
      }

      if (threeLightPreset) {
        threeLightPreset.value = threeSettings.lightPreset;
        threeLightPreset.addEventListener('change', () => {
          stopStory();
          threeSettings.lightPreset = threeLightPreset.value;
          applyLightPreset();
          syncDebugTextareaFromLive();
          setDebugStatus(`Light preset: ${threeSettings.lightPreset}`);
        });
      }

      if (threeFullscreenToggle) {
        syncFullscreenButton(false);
        threeFullscreenToggle.addEventListener("click", () => {
          const entering = !(document.fullscreenElement === container || container.classList.contains("theater-mode"));
          setThreeFullscreen(entering);
        });
        document.addEventListener("fullscreenchange", () => {
          container.classList.toggle("theater-mode", document.fullscreenElement === container);
          syncFullscreenButton(document.fullscreenElement === container);
          onResize();
        });
      }

      threeOrbitButtons.forEach((button) => {
        button.addEventListener("click", () => {
          applyOrbitMode(button.dataset.orbitMode || "free");
        });
      });

      if (threeOrbitToggle) {
        threeOrbitToggle.addEventListener("click", () => {
          applyOrbitMode(orbitMode === "lock" ? "free" : "lock");
        });
      }

      if (threeMoreToggle) {
        threeMoreToggle.addEventListener("click", (event) => {
          event.stopPropagation();
          toggleMoreDrawer();
        });
      }

      if (threeMoreDrawer) {
        threeMoreDrawer.addEventListener("click", (event) => event.stopPropagation());
      }

      document.addEventListener("click", (event) => {
        if (threeViewToolbar && !threeViewToolbar.contains(event.target)) {
          closeMoreDrawer(false);
        }
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeMoreDrawer(false);
      });

      threeViewAnchorButtons.forEach((button) => {
        button.addEventListener("click", () => {
          if (!scene) initThree();
          threeViewAnchorButtons.forEach((entry) => entry.classList.toggle("active", entry === button));
          flyToCamera(cameraAnchor(button.dataset.viewAnchor));
        });
      });

      threeLayerButtons.forEach((button) => {
        button.addEventListener("click", () => {
          setLayerGroup(button.dataset.layerToggle);
        });
      });

      threeTimeSpeedButtons.forEach((button) => {
        button.addEventListener("click", () => {
          timeFlow.speed = Number(button.dataset.timeSpeed) || 1;
          if (timeFlow.direction !== 0) startToolbarTime(timeFlow.direction);
          syncTimeControls();
        });
      });

      threeTimeButtons.forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.dataset.timeAction;
          if (action === "step-back") {
            stopToolbarTime();
            stepToolbarTime(-1);
          } else if (action === "step-forward") {
            stopToolbarTime();
            stepToolbarTime(1);
          } else if (action === "reverse") {
            startToolbarTime(-1);
          } else if (action === "play") {
            startToolbarTime(1);
          } else if (action === "pause") {
            stopToolbarTime();
          } else if (action === "loop") {
            timeFlow.loop = !timeFlow.loop;
            syncTimeControls();
          }
        });
      });

      syncTimeControls();

      if (threeToolbarPin && threeViewToolbar) {
        threeToolbarPin.addEventListener("click", () => {
          const pinned = !threeViewToolbar.classList.contains("pinned");
          threeViewToolbar.classList.toggle("pinned", pinned);
          threeToolbarPin.classList.toggle("active", pinned);
          threeToolbarPin.setAttribute("aria-pressed", pinned ? "true" : "false");
          threeToolbarPin.title = pinned ? "Allow toolbar to fade" : "Keep toolbar visible";
          threeToolbarPin.setAttribute("aria-label", pinned ? "Allow toolbar to fade" : "Keep toolbar visible");
        });
      }


      if (threeDebugCapture) {
        threeDebugCapture.addEventListener('click', () => {
          syncDebugTextareaFromLive();
          setDebugStatus("Captured current view.");
        });
      }

      if (threeDebugApply) {
        threeDebugApply.addEventListener('click', () => {
          stopStory();
          applyThreeSettingsFromTextarea();
        });
      }

      if (threeDebugCopy) {
        threeDebugCopy.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(threeDebugJson.value);
            setDebugStatus("Copied JSON.");
          } catch (_error) {
            setDebugStatus("Copy failed.");
          }
        });
      }

      if (threeDebugReset) {
        threeDebugReset.addEventListener('click', () => {
          stopStory();
          threeSettings = cloneSettings(defaultThreeSettings);
          if (threeLightPreset) threeLightPreset.value = threeSettings.lightPreset;
          applyThreeSettings();
          syncDebugTextareaFromLive();
          setDebugStatus("Restored defaults.");
        });
      }

      if (threeDockToggle && threeDock) {
        const syncDockLayout = () => {
          const collapsed = threeDock.classList.contains("collapsed");
          const workspace = threeDock.closest(".three-workspace");
          workspace?.classList.toggle("dock-collapsed", collapsed);
          if (collapsed && workspace) workspace.style.gridTemplateColumns = "";
          else {
            let savedWidth = null;
            try { savedWidth = Number(window.localStorage.getItem("threeDockWidth")) || null; } catch (error) {}
            if (savedWidth) setDockWidth(savedWidth);
          }
          threeDockToggle.textContent = collapsed ? "Show dock" : "Hide dock";
          window.dispatchEvent(new Event("resize"));
        };
        threeDockToggle.addEventListener("click", () => {
          threeDock.classList.toggle("collapsed");
          syncDockLayout();
        });
        syncDockLayout();
      }

      initDockResizer();
      initVysuEditorChrome();

      threeDockTabs.forEach((button) => {
        button.addEventListener("click", () => setDockTab(button.dataset.dockTab));
      });

      if (threeStorySelect) {
        threeStorySelect.addEventListener("change", () => {
          const story = selectedStoryOriginal();
          if (story && threeStoryEditor) {
            loadStoryIntoEditors(story);
            setStoryStatus("Loaded build-time story.");
          }
        });
      }

      if (threeStorySearch) {
        threeStorySearch.addEventListener("input", () => {
          renderStoryPills();
          renderStoryEditorOptions();
        });
      }

      if (threeStoryRun) {
        threeStoryRun.addEventListener("click", () => {
          try {
            const story = storyFromEditor();
            runStory(story);
            setStoryStatus(`Running ${story.title}.`);
          } catch (error) {
            setStoryStatus(`Invalid story: ${error.message}`);
          }
        });
      }

      if (threeVysuRun) {
        threeVysuRun.addEventListener("click", () => {
          try {
            const compiled = compileVyomaSutra(threeVysuEditor?.value || "");
            threeStoryEditor.value = JSON.stringify(compiled.story, null, 2);
            validateStoryForEditor(compiled.story);
            runStory(compiled.story);
            const warningText = compiled.warnings.length ? ` Warnings: ${compiled.warnings.join(" | ")}` : "";
            setVysuStatus(`Running VyomaSutra.${warningText}`);
            setStoryStatus("JSON updated from VyomaSutra.");
          } catch (error) {
            setVysuStatus(`Invalid VyomaSutra: ${error.message}`);
          }
        });
      }

      if (threeCameraGrab) {
        threeCameraGrab.addEventListener("click", () => {
          if (!scene) initThree();
          grabCameraDirective();
        });
      }

      if (threeStoryStop) {
        threeStoryStop.addEventListener("click", () => {
          stopStory();
          setStoryStatus("Stopped.");
          setVysuStatus("Stopped.");
        });
      }

      if (threeStoryReset) {
        threeStoryReset.addEventListener("click", () => {
          const story = selectedStoryOriginal();
          if (story && threeStoryEditor) {
            stopStory();
            loadStoryIntoEditors(story);
            setStoryStatus("Reloaded original.");
            setVysuStatus("Reloaded story VyomaSutra.");
          }
        });
      }

      if (threeStoryCopy) {
        threeStoryCopy.addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(threeStoryEditor.value);
            setStoryStatus("Copied story JSON.");
          } catch (_error) {
            setStoryStatus("Copy failed.");
          }
        });
      }

      renderStoryPills();
      renderStoryEditorOptions();
      renderThreeDebugToggles();
      syncThreeDebugTogglesFromSettings();
      syncDebugTextareaFromLive();

      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !scene) {
          initThree();
        }
      });
      observer.observe(container);
