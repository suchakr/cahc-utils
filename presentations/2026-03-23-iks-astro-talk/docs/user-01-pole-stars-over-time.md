# `user-01-pole-stars-over-time`

## Status

Method note for discussion and implementation planning.

## Script Target

- Stellarium script: `ssc/user-01-pole-stars-over-time.ssc`

## Motivation

This topic arose from an audience question after the tutorial:

- can the precession circle be visualized clearly in Stellarium?
- can we show that different stars served as pole stars at different epochs?
- can we trace this by method rather than by repeating a static list?

The goal is to answer that question in a way that is visually persuasive, computationally sound, and lightweight enough to support future student-driven follow-ups.

## Problem

We want to identify and display stars that come close to the north celestial pole at different epochs, while making precession itself the central explanatory idea.

This is not just a lookup problem.

The real question is:

- how does the north celestial pole move over time?
- which stars come closest to it, and when?
- how should we show those results clearly to an audience?

## Core Idea

Split the task into two phases:

- Astropy does the scan
- Stellarium does the display

This keeps each tool in the role it is best suited for.

## Why This Split Is Correct

Stellarium is optimized for interactive sky visualization, not catalog mining.

That means it is excellent for:

- showing the precession circle
- jumping to a star and epoch
- letting the audience see sky geometry
- presenting a curated visual tour

But it is not the right place to do a catalog search over many stars and epochs.

The inefficiency concern is real in Stellarium, not in Astropy.

Astropy is the better place to:

- work from a star catalog
- transform coordinates across epochs
- compute angular separation from the moving north celestial pole
- rank stars by closest approach
- generate a compact candidate table for later visualization

So the computational search should happen offline in Astropy, and the resulting shortlist should be handed to Stellarium for visual explanation.

For this topic, the planned low-ceremony source pipeline is:

- fetch Hipparcos once from Vizier
- cache a normalized local copy at `data/hip_main_vizier.tsv`
- run the Astropy scan against that local cache
- emit `ssc/user-01-pole-stars-over-time.ssc`

## Precession Framing

The audience concern should be addressed explicitly:

- the north celestial pole is not fixed against the stars
- due to precession, it moves over time
- this motion traces a circle around the north ecliptic pole
- because of this motion, different stars become better pole-star candidates at different epochs

The method page and eventual script should keep that explanation front and center. The point is not merely to name pole stars, but to show why the identity of the pole star changes.

## Proposed Scan

The Astropy phase should:

1. Fetch the Hipparcos main table from Vizier and cache a normalized local TSV.
2. Choose a practical brightness cutoff.
3. Apply a broad prefilter around the northern precession-circle locus.
4. Compute the north celestial pole as a function of epoch.
5. Compute angular separation from each candidate star to the pole at each epoch.
6. Record, for each HIP, the epoch of closest approach and the minimum distance.
7. Produce a ranked shortlist for display.

This produces a method-derived answer rather than a memorized or copied table.

## Proposed Display

The Stellarium phase should:

1. Show the precession circle visually.
2. Introduce a curated shortlist of candidate pole stars.
3. Jump to key epochs where a candidate approaches the pole closely.
4. Label the star, epoch, and approximate distance from the pole.
5. Make the visual point that the pole moves and the stars do not all serve equally well at all times.

The display script should be light. It should not try to search the catalog on the fly.

## Expected Outputs

The first useful output is a compact candidate table containing fields like:

- star name
- HIP identifier
- brightness
- epoch of closest approach
- minimum angular distance from the north celestial pole

The second useful output is a Stellarium demonstration that walks through the best candidates in a visually intelligible order.

## Scope

In scope:

- north celestial pole
- precession as the explanatory mechanism
- bright or otherwise curated star candidates
- an Astropy-generated shortlist
- a Stellarium visual tour based on that shortlist

Out of scope for the first version:

- scanning the full Stellarium catalog from inside `.ssc`
- making Stellarium itself perform the catalog search
- exhaustive catalog completeness claims
- a full historical essay on all claimed pole stars

## Design Preference

Keep process light and keep attention on method and result.

This means:

- one short method note
- one light Astropy scan script
- one light Stellarium display script
- one candidate table worth discussing

The point is to show a reproducible way of answering the audience question, not to build a large framework.

## Success Criteria

This topic is successful if it does all of the following:

- explains why the pole star changes over time
- makes precession visually understandable
- produces a computed shortlist of candidate pole stars
- uses Stellarium to show the result clearly
- makes it obvious why Astropy is the right tool for the scan

## Next Step

Implement the Astropy scan first, then use its output to design the Stellarium tour in `ssc/user-01-pole-stars-over-time.ssc`.
