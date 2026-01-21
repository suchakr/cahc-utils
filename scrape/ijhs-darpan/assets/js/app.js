/**
 * IJHS Darpan - Application Logic
 * 
 * Core responsibilities:
 * 1. Determine Environment (Local vs Netlify).
 * 2. Load Data (from data.js).
 * 3. Render Filters & Grid.
 * 4. Handle Search & Filter events.
 */

// --- State ---
const State = {
    papers: [], // Source data
    filtered: [], // Current view
    filters: {
        search: "",
        useRegex: false, // New: Toggle state
        categories: new Set(),
        subjects: new Set(),
        decades: new Set()
    },
    // We will compute env strictly in a helper
    env: 'netlify', // 'file', 'localhost', 'netlify'
    theme: localStorage.getItem('ijhs-theme') || 'dark'
};

// --- DOM Elements ---
const Elements = {
    grid: document.getElementById('results-grid'),
    searchInput: document.getElementById('search-input'),
    regexToggle: document.getElementById('regex-toggle'), // New
    categoryFilters: document.getElementById('category-filters'),
    subjectFilters: document.getElementById('subject-filters'),
    decadeFilters: document.getElementById('decade-filters'),
    resultCount: document.getElementById('result-count'),
    emptyState: document.getElementById('empty-state'),
    modeBadge: document.getElementById('mode-badge'),
    menuToggle: document.getElementById('menu-toggle'),
    closeMenu: document.getElementById('close-menu'),
    sidebar: document.getElementById('sidebar'),
    resetBtn: document.getElementById('reset-filters'),
    themeToggle: document.getElementById('theme-toggle')
};

// --- Logic ---

function init() {
    // 1. Detect Env
    detectEnvironment();

    // 2. Load Theme
    applyTheme(State.theme);

    // 3. Load Data
    if (typeof PAPERS === 'undefined') {
        console.error("Data not loaded!");
        return;
    }
    State.papers = PAPERS;
    State.filtered = PAPERS;

    // 4. Setup UI
    updateModeBadge();
    setupFilters();
    renderGrid();

    // 5. Event Listeners
    Elements.searchInput.addEventListener('input', (e) => {
        State.filters.search = e.target.value; // Store raw case for regex
        applyFilters();
    });

    if (Elements.regexToggle) {
        Elements.regexToggle.addEventListener('click', () => {
            State.filters.useRegex = !State.filters.useRegex;
            Elements.regexToggle.classList.toggle('active', State.filters.useRegex);
            applyFilters();
        });
    }

    if (Elements.resetBtn) {
        Elements.resetBtn.addEventListener('click', resetFilters);
    }

    if (Elements.themeToggle) {
        Elements.themeToggle.addEventListener('click', toggleTheme);
    }

    // Mobile Sidebar
    if (Elements.menuToggle && Elements.sidebar) {
        Elements.menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            Elements.sidebar.classList.add('open');
        });
    }

    if (Elements.closeMenu && Elements.sidebar) {
        Elements.closeMenu.addEventListener('click', () => {
            Elements.sidebar.classList.remove('open');
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (Elements.sidebar && Elements.sidebar.classList.contains('open') &&
            !Elements.sidebar.contains(e.target) &&
            !Elements.menuToggle.contains(e.target)) {
            Elements.sidebar.classList.remove('open');
        }
    });
}

// ... helper functions (environment, theme) unchanged ... 
// (For brevity in this tool call, assuming environment/theme helpers are outside the replaced block or I will be careful not to overwrite them if they are within range. 
// Wait, I am replacing a huge chunk. I must include the helpers if they fall within lines 12-246.
// Lines 103-160 contain detectEnvironment, updateModeBadge, getPdfLink, toggleTheme, applyTheme. I MUST include them.)

function detectEnvironment() {
    if (window.location.protocol === 'file:') {
        State.env = 'file';
    } else if (window.location.hostname.includes('localhost') || window.location.hostname.includes('127.0.0.1')) {
        State.env = 'localhost';
    } else {
        State.env = 'netlify';
    }
}

function updateModeBadge() {
    if (State.env === 'file') {
        Elements.modeBadge.textContent = "Local File";
        Elements.modeBadge.className = "badge local";
        Elements.modeBadge.title = "Loaded directly from file system (file://)";
    } else if (State.env === 'localhost') {
        Elements.modeBadge.textContent = "Local Host";
        Elements.modeBadge.className = "badge host"; // Purple style
        Elements.modeBadge.title = "Served via Local Server";
    } else {
        // Netlify / Remote
        Elements.modeBadge.style.display = 'none'; // "no label" as requested
    }
}

function getPdfLink(paper) {
    if (State.env === 'netlify') {
        return paper.remoteUrl;
    }
    // For file or localhost, try local path
    if (paper.localPath) {
        return paper.localPath;
    }
    return paper.remoteUrl;
}

function toggleTheme() {
    State.theme = State.theme === 'dark' ? 'light' : 'dark';
    applyTheme(State.theme);
    localStorage.setItem('ijhs-theme', State.theme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    // Toggle Icons logic (SVG paths handled in HTML, here we toggle classes if needed, 
    // BUT we used .sun-icon / .moon-icon class structure in HTML)
    const sun = Elements.themeToggle.querySelector('.sun-icon');
    const moon = Elements.themeToggle.querySelector('.moon-icon');

    if (theme === 'dark') {
        if (sun) sun.classList.remove('hidden');
        if (moon) moon.classList.add('hidden');
    } else {
        if (sun) sun.classList.add('hidden');
        if (moon) moon.classList.remove('hidden');
    }
}

function resetFilters() {
    State.filters.search = "";
    State.filters.useRegex = false;
    if (Elements.regexToggle) Elements.regexToggle.classList.remove('active');

    State.filters.categories.clear();
    State.filters.subjects.clear();
    State.filters.decades.clear();
    Elements.searchInput.value = "";

    document.querySelectorAll('.checkbox-item input').forEach(el => el.checked = false);

    applyFilters();
}

function setupFilters() {
    const SafeCat = (v) => (!v || v === 'nan' || v === 'NaN' || v === 'Uncategorized') ? "Uncategorized" : v;
    const SafeSub = (v) => (!v || v === 'nan' || v === 'NaN') ? "General" : v;

    const categories = [...new Set(State.papers.map(p => SafeCat(p.category)))].sort();
    const subjects = [...new Set(State.papers.map(p => SafeSub(p.subject)))].sort();

    const decades = [...new Set(State.papers.map(p => {
        const y = parseInt(p.year);
        return isNaN(y) ? null : Math.floor(y / 10) * 10;
    }).filter(Boolean))].sort((a, b) => b - a);

    const decadeStrings = decades.map(d => `${d}s`);

    renderCheckboxList(Elements.categoryFilters, categories, 'categories');
    renderCheckboxList(Elements.subjectFilters, subjects, 'subjects');
    renderCheckboxList(Elements.decadeFilters, decadeStrings, 'decades');
}

function renderCheckboxList(container, items, filterKey) {
    container.innerHTML = '';
    items.forEach(item => {
        const label = document.createElement('label');
        label.className = 'checkbox-item';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = item;
        input.addEventListener('change', (e) => {
            if (e.target.checked) {
                State.filters[filterKey].add(item);
            } else {
                State.filters[filterKey].delete(item);
            }
            applyFilters();
        });

        label.appendChild(input);

        const displayItem = item.length > 28 ? item.substring(0, 26) + '...' : item;
        const text = document.createTextNode(displayItem);
        label.appendChild(text);

        container.appendChild(label);
    });
}

function applyFilters() {
    const term = State.filters.search;
    const useRegex = State.filters.useRegex;
    const cats = State.filters.categories;
    const subs = State.filters.subjects;
    const decs = State.filters.decades;

    const SafeCat = (v) => (!v || v === 'nan' || v === 'NaN' || v === 'Uncategorized') ? "Uncategorized" : v;
    const SafeSub = (v) => (!v || v === 'nan' || v === 'NaN') ? "General" : v;

    // Pre-compile regex if needed
    let regex = null;
    if (term && useRegex) {
        try {
            regex = new RegExp(term, 'i');
        } catch (e) {
            // Invalid regex, treat as empty or don't filter? 
            // Better to show no results or just ignore? 
            // Let's allow partial typing without crashing:
            // logic: if invalid regex, search nothing or just fail gracefully.
            // here we'll just fail the match for everything to indicate error indirectly
            regex = null; // will cause 0 results if we strictly rely on it
        }
    }

    State.filtered = State.papers.filter(p => {
        // 1. Search Filter (Expanded Scope: Title, Author, Subject, Year, Journal)
        if (term) {
            const content = `${p.title} ${p.author} ${p.subject} ${p.year} ${p.journal}`;

            if (useRegex) {
                if (!regex || !regex.test(content)) return false;
            } else {
                // Smart Search: AND logic (all terms must be present)
                const terms = term.toLowerCase().split(/\s+/).filter(t => t.length > 0);
                const contentLower = content.toLowerCase();
                const matchesAll = terms.every(t => contentLower.includes(t));
                if (!matchesAll) return false;
            }
        }

        // 2. Category Filter
        if (cats.size > 0 && !cats.has(SafeCat(p.category))) return false;

        // 3. Subject Filter
        if (subs.size > 0 && !subs.has(SafeSub(p.subject))) return false;

        // 4. Decade Filter
        if (decs.size > 0) {
            const year = parseInt(p.year);
            const decade = isNaN(year) ? 'Unknown' : `${Math.floor(year / 10) * 10}s`;
            if (!decs.has(decade)) return false;
        }

        return true;
    });

    renderGrid();
}

function renderGrid() {
    const container = Elements.grid;
    container.innerHTML = '';

    Elements.resultCount.innerText = State.filtered.length;

    if (State.filtered.length === 0) {
        Elements.emptyState.classList.remove('hidden');
        return;
    } else {
        Elements.emptyState.classList.add('hidden');
    }

    const renderLimit = 100;
    const slice = State.filtered.slice(0, renderLimit);

    const SafeCat = (v) => (!v || v === 'nan' || v === 'NaN' || v === 'Uncategorized') ? "Uncategorized" : v;
    const SafeSub = (v) => (!v || v === 'nan' || v === 'NaN') ? "General" : v;

    slice.forEach(paper => {
        const cat = SafeCat(paper.category);
        const sub = SafeSub(paper.subject);

        const card = document.createElement('a');
        const catClass = `cat-${cat.replace(/[^a-zA-Z0-9]/g, '-')}`;

        card.className = `paper-card ${catClass}`;
        card.href = getPdfLink(paper);
        card.target = '_blank';
        card.rel = 'noopener noreferrer';

        card.innerHTML = `
            <div class="paper-meta">
                <span class="paper-year">${paper.year}</span>
                <span class="paper-category">${cat} / ${sub}</span>
            </div>
            <h3 class="paper-title">${paper.title}</h3>
            <div class="paper-author">${paper.author}</div>
            <div class="paper-footer">
                <span>${paper.journal}</span>
                <span>${Math.round(paper.size / 1024 * 10) / 10} MB</span>
            </div>
        `;
        container.appendChild(card);
    });

    if (State.filtered.length > renderLimit) {
        const more = document.createElement('div');
        more.style.gridColumn = "1 / -1";
        more.style.textAlign = "center";
        more.style.padding = "20px";
        more.style.color = "var(--text-secondary)";
        more.innerText = `...and ${State.filtered.length - renderLimit} more results. Refine your search.`;
        container.appendChild(more);
    }
}

// Start
init();
