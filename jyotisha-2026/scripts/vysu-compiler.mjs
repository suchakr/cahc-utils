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

export function compileVyomaSutra(source, options = {}) {
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

export function validateStory(story) {
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

export function compileVyomaSutraFile(source, storyId) {
  return compileVyomaSutra(source, { storyId }).story;
}
