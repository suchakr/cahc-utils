      import * as THREE from 'three';
      import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

      const data = JSON.parse(document.getElementById("explorer-data").textContent);
      const stories = JSON.parse(document.getElementById("story-data").textContent);
      const container = document.getElementById("three-container");
      const threeFullscreenToggle = document.getElementById("three-fullscreen-toggle");
      const overlayLabel = document.getElementById("three-epoch-label");
      const storyStrip = document.getElementById("three-story-strip");
      const storyCaption = document.getElementById("three-story-caption");
      const threeDock = document.getElementById("three-dock");
      const threeDockToggle = document.getElementById("three-dock-toggle");
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
      const threeVysuRun = document.getElementById("three-vysu-run");
      const threeVysuStatus = document.getElementById("three-vysu-status");
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
      let builtEclipticGridStep = null;
      let builtEquatorialGridStep = null;
      const activeTransitionTargets = new Set();
      const activeTransitionObjects = new Set();
      const targetVisibilityOverrides = new Map();
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
        return sprite;
      }

      function setSpriteHeight(sprite, height) {
        const aspect = sprite?.userData?.aspect || 1;
        sprite.scale.set(height * aspect, height, 1);
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

      function cloneSettings(settings) {
        return JSON.parse(JSON.stringify(settings));
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
        if (threeFullscreenToggle) {
          threeFullscreenToggle.textContent = enabled ? "Esc to Minimize" : "Fullscreen";
        }
        window.setTimeout(onResize, 80);
      }

      function applyStoryState(patch) {
        const preserveEpoch = !Object.prototype.hasOwnProperty.call(patch || {}, "epochYear");
        const preserveCamera = !(patch || {}).camera;
        mergeSettings(threeSettings, patch || {});
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
                  const scale = 1 + 0.18 * wave;
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
          NEP: { ui: { showNEP: visible } },
          SEP: { ui: { showSEP: visible } },
          eclipticNakSegments: { ui: { showEclipticBand: visible, showEclipticDividers: visible, showEclipticLabels: visible, showEclipticPoles: visible } },
          stars: { ui: { showStars: visible } },
          nakshatras: { ui: { showNakshatraLines: visible, showNakshatraLabels: visible } },
          nakshatraLines: { ui: { showNakshatraLines: visible } },
          nakshatraLabels: { ui: { showNakshatraLabels: visible } },
          polarItems: { ui: { showPolarItems: visible } },
          northPolarItems: { ui: { showPolarItems: true, showNorthPolarItems: visible } },
          southPolarItems: { ui: { showPolarItems: true, showSouthPolarItems: visible } },
          poleTrack: { ui: { showPoleTrack: visible } },
          precessionCircle: { ui: { showPoleTrack: visible } },
          seasonalFrame: { ui: { showSeasonalFrame: visible } },
          NP: { ui: { showNP: visible } },
          SP: { ui: { showSP: visible } },
          overlay: { ui: { showOverlay: visible } },
        };
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
      data.nakshatras.forEach((row) => {
        const abbr = normalizeNakKey((row.nid || "").split("-").pop());
        const english = normalizeNakKey(row.enaks);
        const index = String(row.sector_index_27 || row.meta_index_28).padStart(2, "0");
        [abbr, english, `n${index}`].forEach((alias) => {
          if (alias) nakAliasMap.set(alias, row.nid);
        });
      });
      Object.entries({
        pph: "N11-PPhal", uph: "N12-UPhal", pas: "N20-PAsh", uas: "N21-UAsh",
        ppr: "N25-PPros", pbh: "N25-PPros", upr: "N26-UPros", ubh: "N26-UPros",
        abh: "N28-Abh", n28: "N28-Abh",
      }).forEach(([alias, nid]) => nakAliasMap.set(alias, nid));

      function resolveNakshatraTarget(target) {
        const raw = String(target || "");
        if (!/^[$*@]/.test(raw)) return null;
        const sigil = raw[0];
        const query = normalizeNakKey(raw.slice(1));
        if (nakAliasMap.has(query)) return { sigil, nid: nakAliasMap.get(query) };
        const matches = Array.from(nakAliasMap.entries()).filter(([alias]) => alias.startsWith(query));
        if (matches.length === 1) return { sigil, nid: matches[0][1] };
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
        const nakTarget = resolveNakshatraTarget(target);
        if (nakTarget) {
          const items = [];
          if (nakTarget.sigil === "$" || nakTarget.sigil === "@") {
            const row = data.nakshatras.find((item) => item.nid === nakTarget.nid);
            const sectorIndex = row?.sector_index_27;
            if (sectorIndex !== null && sectorIndex !== undefined) {
              const index = data.nakshatras.filter((item) => item.sector_index_27 !== null).findIndex((item) => item.nid === nakTarget.nid);
              if (bandRefs.meshes[index]) items.push({ object: bandRefs.meshes[index], opacity: threeSettings.ecliptic.bandOpacity });
              if (bandRefs.dividers[index]) items.push({ object: bandRefs.dividers[index], opacity: threeSettings.ecliptic.dividerOpacity });
              if (bandRefs.labels[index]) items.push({ object: bandRefs.labels[index], opacity: threeSettings.ecliptic.sectorLabelOpacity });
            }
          }
          if (nakTarget.sigil === "*" || nakTarget.sigil === "@") {
            nakshatraLineRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {
              items.push({ object: entry.line, opacity: threeSettings.nakshatras.selectedOpacity });
            });
            nakshatraLabelRefs.filter((entry) => entry.nid === nakTarget.nid).forEach((entry) => {
              items.push({ object: entry.sprite, opacity: threeSettings.nakshatras.labelOpacity });
            });
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
          ];
        }
        if (target === "precessionCircle") {
          return poleTrackCircle ? [transitionDescriptor(poleTrackCircle, threeSettings.poleTrack.opacity, 0)] : [];
        }
        if (target === "seasonalFrame") {
          return [
            ...(equatorLine ? [transitionDescriptor(equatorLine, threeSettings.seasonal.equatorOpacity, 0)] : []),
            ...(poleDot ? [transitionDescriptor(poleDot, 1, 1)] : []),
            ...(movingPoleLabel ? [transitionDescriptor(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelOpacity, 2)] : []),
            ...seasonalMarkerRefs.flatMap((entry, index) => [
              transitionDescriptor(entry.mesh, 1, index + 3),
              transitionDescriptor(entry.sprite, threeSettings.seasonal.markerLabelOpacity, index + 3.1),
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
        applyLightPreset();
        if (siderealGroup && builtEclipticGridStep !== gridStep(threeSettings.grid.eclipticStepDeg)) {
          buildSphereGrid();
        }
        if (seasonalGroup && builtEquatorialGridStep !== gridStep(threeSettings.grid.equatorialStepDeg)) {
          buildEquatorialGrid();
        }

        gridRefs.parallels.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.parallelColor);
          line.material.opacity = threeSettings.grid.parallelOpacity;
        });
        gridRefs.meridians.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.meridianColor);
          line.material.opacity = threeSettings.grid.meridianOpacity;
        });
        gridRefs.equatorialParallels.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.equatorialColor);
          line.material.opacity = threeSettings.grid.equatorialOpacity;
        });
        gridRefs.equatorialMeridians.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.material.color.set(threeSettings.grid.equatorialColor);
          line.material.opacity = threeSettings.grid.equatorialOpacity;
        });

        if (eclipticPlane) {
          eclipticPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEclipticPlane !== false;
          eclipticPlane.material.color.set(threeSettings.reference.eclipticPlaneColor);
          eclipticPlane.material.opacity = threeSettings.reference.eclipticPlaneOpacity;
        }
        if (equatorialPlane) {
          equatorialPlane.visible = threeSettings.ui.showReferencePlanes && threeSettings.ui.showEquatorialPlane !== false;
          equatorialPlane.material.color.set(threeSettings.reference.equatorialPlaneColor);
          equatorialPlane.material.opacity = threeSettings.reference.equatorialPlaneOpacity;
        }
        if (nsAxisLine) {
          nsAxisLine.visible = threeSettings.ui.showNsAxis;
          nsAxisLine.material.color.set(threeSettings.reference.nsAxisColor);
          nsAxisLine.material.opacity = threeSettings.reference.nsAxisOpacity;
        }

        bandRefs.meshes.forEach((mesh) => {
          if (activeTransitionObjects.has(mesh)) return;
          mesh.visible = threeSettings.ui.showEclipticBand;
          mesh.material.opacity = threeSettings.ecliptic.bandOpacity;
        });
        bandRefs.dividers.forEach((line) => {
          if (activeTransitionObjects.has(line)) return;
          line.visible = threeSettings.ui.showEclipticDividers;
          line.material.opacity = threeSettings.ecliptic.dividerOpacity;
        });
        bandRefs.labels.forEach((label) => {
          if (activeTransitionObjects.has(label)) return;
          label.visible = threeSettings.ui.showEclipticLabels;
          label.material.opacity = threeSettings.ecliptic.sectorLabelOpacity;
          setSpriteHeight(label, threeSettings.ecliptic.sectorLabelSize);
        });
        eclipticPoleLabels.forEach((label) => {
          if (activeTransitionObjects.has(label)) return;
          const isSep = label.name === "SEP";
          label.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
          label.material.opacity = threeSettings.ecliptic.poleLabelOpacity;
          setSpriteHeight(label, threeSettings.ecliptic.poleLabelSize);
        });
        eclipticPoleDots.forEach((dot) => {
          if (activeTransitionObjects.has(dot)) return;
          const isSep = dot.name === "SEP";
          dot.visible = threeSettings.ui.showEclipticPoles && (isSep ? threeSettings.ui.showSEP !== false : threeSettings.ui.showNEP !== false);
        });
        if (eclipticCircle) {
          if (!activeTransitionObjects.has(eclipticCircle)) {
            eclipticCircle.visible = threeSettings.ui.showEclipticBand;
            eclipticCircle.material.color.set(threeSettings.ecliptic.circleColor);
            eclipticCircle.material.opacity = threeSettings.ecliptic.circleOpacity;
          }
        }

        starGroupRefs.forEach((entry) => {
          if (activeTransitionObjects.has(entry.points)) return;
          entry.points.visible = threeSettings.ui.showStars;
          entry.points.material.size = threeSettings.stars.size;
          entry.points.material.opacity = threeSettings.stars.opacity;
        });

        if (poleTrackCircle) {
          poleTrackCircle.visible = threeSettings.ui.showPoleTrack;
          poleTrackCircle.material.color.set(threeSettings.poleTrack.color);
          poleTrackCircle.material.opacity = threeSettings.poleTrack.opacity;
        }
        if (poleTrackArc) {
          poleTrackArc.visible = threeSettings.ui.showPoleTrack;
          poleTrackArc.material.color.set(threeSettings.poleTrack.arcColor);
          poleTrackArc.material.opacity = threeSettings.poleTrack.arcOpacity;
        }
        if (poleTrackLabel) {
          poleTrackLabel.visible = threeSettings.ui.showPoleTrack;
          poleTrackLabel.material.opacity = threeSettings.poleTrack.trackLabelOpacity;
          setSpriteHeight(poleTrackLabel, threeSettings.poleTrack.trackLabelSize);
        }
        if (poleDot) {
          poleDot.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showNP !== false;
          poleDot.material.color.set(threeSettings.poleTrack.dotColor);
        }
        if (movingPoleLabel) {
          movingPoleLabel.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showNP !== false;
          movingPoleLabel.material.opacity = threeSettings.poleTrack.movingPoleLabelOpacity;
          setSpriteHeight(movingPoleLabel, threeSettings.poleTrack.movingPoleLabelSize);
        }
        if (southPoleDot) {
          southPoleDot.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showSP !== false;
          southPoleDot.material.color.set(threeSettings.poleTrack.dotColor);
        }
        if (southPoleLabel) {
          southPoleLabel.visible = threeSettings.ui.showSeasonalFrame && threeSettings.ui.showSP !== false;
          southPoleLabel.material.opacity = threeSettings.poleTrack.movingPoleLabelOpacity * 0.72;
          setSpriteHeight(southPoleLabel, threeSettings.poleTrack.movingPoleLabelSize * 0.9);
        }
        if (equatorLine) {
          equatorLine.visible = threeSettings.ui.showSeasonalFrame && targetVisible("equator");
          equatorLine.material.color.set(threeSettings.seasonal.equatorColor);
          equatorLine.material.opacity = threeSettings.seasonal.equatorOpacity;
        }
        seasonalMarkerRefs.forEach((entry) => {
          const markerVisible = threeSettings.ui.showSeasonalFrame && targetVisible(entry.key);
          entry.mesh.visible = markerVisible;
          entry.sprite.visible = markerVisible;
          entry.mesh.scale.setScalar(threeSettings.seasonal.markerScale);
          entry.sprite.material.opacity = threeSettings.seasonal.markerLabelOpacity;
          setSpriteHeight(entry.sprite, threeSettings.seasonal.markerLabelSize * threeSettings.seasonal.markerScale);
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
            entry.line.visible = visible;
            entry.line.material.color.set(active ? threeSettings.nakshatras.selectedColor : threeSettings.nakshatras.color);
            entry.line.material.opacity = visible ? (active ? threeSettings.nakshatras.selectedOpacity : threeSettings.nakshatras.opacity) : 0;
          });
        }
        if (!transitioningNakshatras && !activeTransitionTargets.has("nakshatraLabels")) {
          nakshatraLabelRefs.forEach((entry) => {
            if (activeTransitionObjects.has(entry.sprite)) return;
            const visible = threeSettings.ui.showNakshatraLabels && st.visibleNakshatras[entry.nid] !== false;
            entry.sprite.visible = visible;
            entry.sprite.material.opacity = visible ? threeSettings.nakshatras.labelOpacity : 0;
            setSpriteHeight(entry.sprite, threeSettings.nakshatras.labelSize);
          });
        }
        if (!activeTransitionTargets.has("stars")) {
          starGroupRefs.forEach((entry) => {
            if (activeTransitionObjects.has(entry.points)) return;
            const visible = threeSettings.ui.showStars && (entry.nid === "__special__" || st.visibleNakshatras[entry.nid] !== false);
            entry.points.visible = visible;
            entry.points.material.opacity = visible ? threeSettings.stars.opacity : 0;
          });
        }
        polarItemRefs.forEach((entry) => {
          const regionVisible = entry.region === "south"
            ? threeSettings.ui.showSouthPolarItems !== false
            : threeSettings.ui.showNorthPolarItems !== false;
          const visible = threeSettings.ui.showPolarItems && regionVisible && aliasesVisible(entry.aliases) && st.visibleCodex[entry.id] !== false;
          entry.object.visible = visible;
          if (entry.object.material) {
            if (entry.kind === "line") entry.object.material.opacity = threeSettings.polarItems.opacity;
            if (entry.kind === "dot") entry.object.material.opacity = threeSettings.polarItems.starOpacity;
            if (entry.kind === "label") {
              entry.object.material.opacity = threeSettings.polarItems.labelOpacity;
              setSpriteHeight(entry.object, threeSettings.polarItems.labelSize);
            }
          }
        });
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
        overlayLabel.textContent = epoch.label;
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
        threeFullscreenToggle.addEventListener("click", () => {
          const entering = !(document.fullscreenElement === container || container.classList.contains("theater-mode"));
          setThreeFullscreen(entering);
        });
        document.addEventListener("fullscreenchange", () => {
          container.classList.toggle("theater-mode", document.fullscreenElement === container);
          threeFullscreenToggle.textContent = document.fullscreenElement === container ? "Esc to Minimize" : "Fullscreen";
          onResize();
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
          threeDock.closest(".three-workspace")?.classList.toggle("dock-collapsed", collapsed);
          threeDockToggle.textContent = collapsed ? "Show dock" : "Hide dock";
          window.dispatchEvent(new Event("resize"));
        };
        threeDockToggle.addEventListener("click", () => {
          threeDock.classList.toggle("collapsed");
          syncDockLayout();
        });
        syncDockLayout();
      }

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
