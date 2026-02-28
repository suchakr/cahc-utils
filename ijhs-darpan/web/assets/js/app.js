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
        useRegex: false,
        sort: "newest", // New
        categories: new Set(),
        subjects: new Set(),
        decades: new Set()
    },
    // We will compute env strictly in a helper
    env: 'netlify', // 'file', 'localhost', 'netlify', 'netlify_dev'
    devMode: localStorage.getItem('ijhs-dev-mode') || 'simulation', // 'simulation' vs 'local'
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

    // Apply default filters (sorting) immediately
    applyFilters();
    // renderGrid is called inside applyFilters, so we don't need to call it explicitly here

    // 5. Event Listeners
    Elements.searchInput.addEventListener('input', (e) => {
        State.filters.search = e.target.value; // Store raw case for regex
        applyFilters();
    });

    // Sort Dropdown
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            State.filters.sort = e.target.value;
            applyFilters();
        });
    }

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

    // Mode Badge Toggle (Simulation vs Local)
    if (Elements.modeBadge) {
        Elements.modeBadge.addEventListener('click', () => {
            if (State.env === 'netlify_dev') {
                State.devMode = State.devMode === 'simulation' ? 'local' : 'simulation';
                localStorage.setItem('ijhs-dev-mode', State.devMode);
                updateModeBadge();
                applyFilters(); // Re-render grid to update links
            }
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
    } else if (window.location.port === '8888') {
        State.env = 'netlify_dev';
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
        Elements.modeBadge.style.cursor = 'default';
        Elements.modeBadge.title = "Loaded directly from file system (file://)";
    } else if (State.env === 'localhost') {
        Elements.modeBadge.textContent = "Local Mode";
        Elements.modeBadge.className = "badge host"; // Purple style
        Elements.modeBadge.style.cursor = 'default';
        Elements.modeBadge.title = "Served via Local Server";
    } else if (State.env === 'netlify_dev') {
        const isSim = State.devMode === 'simulation';
        Elements.modeBadge.textContent = isSim ? "Simulation Mode" : "Local Mode";
        Elements.modeBadge.className = isSim ? "badge host" : "badge local"; 
        Elements.modeBadge.style.cursor = 'pointer';
        Elements.modeBadge.title = isSim ? "Click to switch to Local Files" : "Click to switch to Simulation (GCS)";
    } else {
        // Netlify / Remote
        Elements.modeBadge.style.display = 'none'; 
    }
}

/**
 * Gets the "Mirror" or "Archive" link (GCS via Netlify Function).
 */
function getArchivedLink(paper) {
    if (State.env === 'netlify' || (State.env === 'netlify_dev' && State.devMode === 'simulation')) {
        const filename = paper.remoteUrl.split('/').pop().split('?')[0];
        return `/.netlify/functions/authorize-pdf?file=${encodeURIComponent('assets/ijhs/' + filename)}`;
    }
    // If we are in local mode, the archive link is redundant if we already have localPath,
    // but we can return the remoteUrl as a backup.
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
    State.filters.sort = "newest"; // Reset sort

    // Reset Sort UI
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) sortSelect.value = "newest";

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
    const sortMode = State.filters.sort || 'newest';

    const SafeCat = (v) => (!v || v === 'nan' || v === 'NaN' || v === 'Uncategorized') ? "Uncategorized" : v;
    const SafeSub = (v) => (!v || v === 'nan' || v === 'NaN') ? "General" : v;

    // Pre-compile regex if needed
    let regex = null;
    if (term && useRegex) {
        try {
            regex = new RegExp(term, 'i');
        } catch (e) {
            regex = null;
        }
    }

    State.filtered = State.papers.filter(p => {
        // 1. Search Filter (Expanded Scope: Title, Author, Subject, Year, Journal)
        if (term) {
            const juKeywords = p.juUrl ? "JU Jain University juni" : "";
            const content = `${p.title} ${p.author} ${p.subject} ${p.year} ${p.journal} ${juKeywords}`;

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

    // 5. Sort Logic
    // Helper to extract comparable value from journal string (e.g. IJHS-1-1966-Issue-1)
    // We want Issue 3 > Issue 2 > Issue 1
    const getIssueVal = (j) => {
        if (!j) return 0;
        const match = j.match(/Issue-(\d+)/i);
        return match ? parseInt(match[1]) : 0;
    };

    State.filtered.sort((a, b) => {
        if (sortMode === 'newest') {
            const yA = parseInt(a.year) || 0;
            const yB = parseInt(b.year) || 0;
            if (yA !== yB) return yB - yA; // Primary: Year Desc
            return getIssueVal(b.journal) - getIssueVal(a.journal); // Secondary: Issue Desc
        }
        if (sortMode === 'oldest') {
            const yA = parseInt(a.year) || 0;
            const yB = parseInt(b.year) || 0;
            if (yA !== yB) return yA - yB; // Primary: Year Asc
            return getIssueVal(a.journal) - getIssueVal(b.journal); // Secondary: Issue Asc
        }
        if (sortMode === 'title') return a.title.localeCompare(b.title);
        if (sortMode === 'size') return (a.size || 0) - (b.size || 0); // Smallest first
        if (sortMode === 'relevance') {
            if (!term) return 0;
            const aTitle = a.title.toLowerCase().includes(term.toLowerCase());
            const bTitle = b.title.toLowerCase().includes(term.toLowerCase());
            return bTitle - aTitle;
        }
        return 0;
    });

    renderGrid();
}

function highlightText(text, term, useRegex) {
    if (!term || !text) return text;
    const safeText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    try {
        if (useRegex) {
            const regex = new RegExp(`(${term})`, 'gi');
            return safeText.replace(regex, '<mark>$1</mark>');
        } else {
            const words = term.split(/\s+/).filter(w => w.length > 0);
            if (words.length === 0) return safeText;
            const pattern = words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
            const regex = new RegExp(`(${pattern})`, 'gi');
            return safeText.replace(regex, '<mark>$1</mark>');
        }
    } catch (e) { return safeText; }
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

    const term = State.filters.search;
    const useRegex = State.filters.useRegex;

    slice.forEach(paper => {
        const cat = SafeCat(paper.category);
        const sub = SafeSub(paper.subject);

        // Determine Links based on Mode
        let primaryLink, backupLink;
        const isLocalMode = (State.env === 'localhost' || State.env === 'file' || (State.env === 'netlify_dev' && State.devMode === 'local'));

        if (isLocalMode) {
            // Local Mode: Priortize local copy for "Read", remote for "Archive/Backup"
            primaryLink = paper.localPath || paper.remoteUrl;
            backupLink = paper.remoteUrl;
        } else {
            // Simulation/Remote: Remote for "Read", GCS for "Archive/Backup"
            primaryLink = paper.remoteUrl;
            backupLink = getArchivedLink(paper);
        }

        const isExternal = true; 

        // Use DIV instead of A to support nested interactive elements (Backup Button)
        const card = document.createElement('div');
        const catClass = `cat-${cat.replace(/[^a-zA-Z0-9]/g, '-')}`;

        card.className = `paper-card ${catClass}`;

        // Make the whole card clickable for Primary Link
        card.onclick = (e) => {
            // Check if text validation was selected text, if so don't click
            if (window.getSelection().toString().length > 0) return;
            window.open(primaryLink, '_blank', 'noopener,noreferrer');
        };

        const titleHtml = highlightText(paper.title, term, useRegex);
        const authorHtml = highlightText(paper.author, term, useRegex);
        const yearHtml = highlightText(String(paper.year), term, useRegex);

        // Primary Read Button (Bold)
        // Note: Card click also goes here, but this is the visual CTA
        const readBtn = `
             <a href="${primaryLink}" 
               class="read-link" 
               target="_blank" 
               rel="noopener noreferrer"
               onclick="event.stopPropagation();">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                <span>Read</span>
            </a>
        `;

        // Backup Button (Subtle Archive Icon)
        const backupBtn = `
            <a href="${backupLink}" 
               class="backup-link" 
               target="_blank" 
               rel="noopener noreferrer"
               title="View Archived Copy (Mirror)"
               onclick="event.stopPropagation();">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
            </a>
        `;

        // High Speed Mirror (JU) if available (and if not already primary/backup)
        let juBtn = "";
        if (paper.juUrl && paper.juUrl !== primaryLink && paper.juUrl !== backupLink) {
            juBtn = `
                <div class="vr-sep"></div>
                <a href="${paper.juUrl}" 
                   class="backup-link" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   title="High Speed Mirror (JU)"
                   onclick="event.stopPropagation();">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 16 16 12 12 8"></polyline><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                </a>
            `;
        }

        const juBadge = paper.juUrl ? `<span class="badge ju">JU</span>` : "";
        card.innerHTML = `
            <div class="paper-meta">
                <span class="paper-year">${yearHtml}${juBadge}</span>
                <span class="paper-category">${cat} / ${sub}</span>
            </div>
            <h3 class="paper-title">${titleHtml}</h3>
            <div class="paper-author">${authorHtml}</div>
            <div class="paper-footer">
                <span>${paper.journal}</span>
                <div class="footer-right">
                    <span class="size-info">${Math.round(paper.size / 1024 * 10) / 10} MB</span>
                    ${readBtn}
                    <div class="vr-sep"></div>
                    ${backupBtn}
                    ${juBtn}
                </div>
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
