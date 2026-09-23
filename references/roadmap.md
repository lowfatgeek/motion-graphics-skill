# Roadmap — Development Guidelines and System Evolution

This document tracks the origin, validated foundations, and future evolution of the Motion Bang Bang skill for both human maintainers and AI coding agents.

## Core Design Principle

The rules in `anti-ppt.md` and techniques in `techniques.md` originated from a single fundamental challenge: generated web animations repeatedly felt like corporate presentation slides.
**Only generalized, production-tested principles enter this skill** — never project-specific brand assets, colors, or copy.

## Validated Foundations (Non-Negotiable Baselines)

Do not regress on any of these core architectural decisions:
- **One statement + maximum one hero object per scene**.
- **Unified camera rig (`#world`)**: The background scales and translates in perspective alongside foreground subjects; push-through used only when narratively motivated.
- **Rationed climax effects**: 3D per-word tracking and complex transitions reserved for 1–2 key climax moments.
- **Directional motion blur**: Implemented via SVG filters on entrance/exit tweens.
- **Strict determinism**: All animations calculated strictly as a pure mathematical function of master timeline time (`tl.time()`), enabling frame-accurate scrubbing and export.
- **Visual verification protocol**: Mandatory inspection of keyframe contact sheets prior to presenting deliverables.
- **Authentic brand extraction**: Official vector paths, color tokens, and product claims extracted from verified sources rather than invented.

## Strategic Roadmap

1. **Precomputed Audio Analysis**:
   - Transition from procedural BPM sine approximations to offline FFT audio analysis.
   - Load audio $\rightarrow$ precalculate FFT frequency bins per frame offline $\rightarrow$ serialize to JSON $\rightarrow$ pass into deterministic render loop. Never execute real-time FFT analysis inside the render loop, which breaks scrubbing and frame export.
2. **Expanded Transition Vocabulary**:
   - Add horizontal whip-pans, camera rig rolls, rack-focus blurs, geometric match-cuts, and letterform zoom portals to complement existing push-through and light leaks.
3. **Menu of Concepts, Never Prescriptive Templates**:
   - Avoid standardized rundown templates (e.g. hook $\rightarrow$ feature $\rightarrow$ feature $\rightarrow$ promise $\rightarrow$ CTA), which result in identical structures. Continue expanding the menu in `opener-konsep.md` with diverse conceptual models.
4. **Modular Multi-File Starters**:
   - While `assets/starter-opener.html` is single-file for portability, provide modular folder templates as agent environments evolve.
5. **Enhanced Video Export Pipelines**:
   - Explore WebCodecs `VideoEncoder` and headless `canvas.captureStream` alongside existing Puppeteer pipelines, plus vertical (9:16) rendering presets.
6. **Automated Review Tooling**:
   - Automated scripts that capture $N$ key timestamps (`tl.time(t)`) and generate composite contact sheets for rapid visual inspection.
7. **Failure/Remedy Library Expansion**:
   - Continuously update the anti-pattern table in `anti-ppt.md` with real failure cases and their exact architectural fixes.

## Tempting Anti-Patterns to Avoid

- **Overly finished starter templates**: Starters with complete narrative examples cause AI models to copy structures verbatim. Starters must remain structurally bare and unopinionated regarding scene order.
- **Single "correct" answers per failure**: Providing a single fix turns that fix into a new template. Always offer a menu of diverse solutions.
- **Feature and effect inflation**: Every visual technique must serve camera choreography or narrative revelation. Gimmicky effects age rapidly.
- **Rules without rationales**: Enforce rules by documenting the specific failure modes that produced them. Directives without context are frequently discarded by LLMs.
- **Library lock-in**: GSAP and Three.js are practical defaults, not dogmas. The core principles (anti-PPT, camera rigs, determinism) apply equally to Remotion, Motion One, or pure Canvas.

## Portability Across AI Agents

This repository is fully portable: `SKILL.md`, `references/`, `assets/`, and `scripts/` consist strictly of standard Markdown, HTML, and scripts.
When integrating with an agent lacking native skill folder support:
1. Inject `SKILL.md` into the system prompt.
2. Provide `anti-ppt.md` and `techniques.md` during design sessions.
3. Provide `architecture.md` and the appropriate starter template during coding sessions.
