# Conventions

- Slugs should be short, lowercase, and hyphenated.
- Exploration outputs belong under `lab/<slug>/`.
- Stable reusable code belongs under `src/jyotisha_2026/`.
- Exploration-specific runnable entrypoints belong under `scripts/`.
- From the repository root `cahc-utils/jyotisha-2026`, use `netlify dev --dir lab` for local browser testing of the published lab surface.
- In tabbed exploration pages, the tab label is usually sufficient; avoid repeating the same view name as a bold in-body section heading.
- Current `nakshatra-precession-explorer` QA note: Bharaṇī's displayed star/shape looks wrong, and Dhaniṣṭhā may have a similar join/geometry issue. Re-verify those asterism mappings before using the 2D geometry as the 3D source of truth.
