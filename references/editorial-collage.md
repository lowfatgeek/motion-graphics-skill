# Style 7 — Editorial Collage (Mixed-Media Journalism / Vox Style)

Editorial Collage is an explainer motion graphics style designed for **journalistic investigation, geopolitics, macroeconomic analysis, and modern history**. Unlike Style 2 (Visual Journalism) which operates on a pitch-black canvas with film grain, Editorial Collage operates on a **high-key textured cream grid paper canvas**, balancing tactile print-media archival artifacts (newspapers, halftone dot shaders, paper cutouts) with clean digital data visualization (animated SVG line charts, floating metric cards, animated odometers, and kinetic typewriter typography).

---

## 1. Visual Taxonomy & Design System

| Dimension | Specification | Notes & CSS Implementation |
|---|---|---|
| **Canvas Background** | `#D8D6D0` / `#DCD9D2` with subtle paper fiber texture | Warm parchment paper texture preventing flat digital sterilization. |
| **Architectural Grid** | `#C8C5BF` at 35–45% opacity, 40px × 40px grid squares | Provides an analytical, blueprint-style anchor across all scenes. |
| **Silhouette Shadow Accent** | `#CA4D2D` (Cinnabar / Terracotta Red) | Solid color silhouette offset $X: -18\text{px}, Y: -14\text{px}$ behind desaturated photo cutouts. |
| **Brand & Metric Accent** | `#F9860B` (Amber Orange) | Highlights key metrics, data lines, badges, and the global bottom progress bar. |
| **Highlighter Stroke** | `#EFBC22` (Golden Yellow) with `mix-blend-mode: multiply` | Sweeps across critical keywords in newspaper articles synced to the voiceover. |
| **Primary Typography** | High-contrast Serif (`Playfair Display Black` / `Didot`) | Used for newspaper mastheads, major investigative headlines. |
| **Data Typography** | Heavy Geometric Sans (`Montserrat Black` / `Inter ExtraBold`) | All-caps, tight tracking (`letter-spacing: -0.02em`), soft drop shadow. |
| **Climax Typography** | Monospace Typewriter (`Courier New` / `Special Elite`) | Staggered character reveal with blinking block cursor (`█`). |
| **Dialogue Bubbles** | Bold Condensed Display (`Impact` / `Bangers`) | White comic speech bubbles with crisp 3px black borders and directional tail. |
| **Global Progress Bar** | Bottom edge, 48px height, solid `#F9860B` | Starts at 0% and expands linearly to 100% across the total video duration. |

---

## 2. Core Motion Principles & Physics

### 2.1 The Two Transition Modes
1. **Hard Cut (Chapter Shift)**:
   - When jumping between major narrative chapters (e.g. Political Introduction $\rightarrow$ Newspaper Evidence $\rightarrow$ Macroeconomic Event $\rightarrow$ Philosophical Conclusion), execute a **1-frame direct hard cut**. Avoid dissolves or generic crossfades.
2. **Continuous Camera Translation (Data Connection)**:
   - When illustrating relationships between data points (e.g. Inflation Chart $\rightarrow$ \$39 Trillion Debt Map $\rightarrow$ Budget Comparison Figures), the camera smoothly translates horizontally or scales across a persistent world stage using `power2.inOut` or `power3.inOut`.

### 2.2 Occlusion and Staggered Entrance
- **Pop-Up from Occluders**: Character cutouts do not pop out of thin air; they slide up (`power2.out`) from behind architectural elements or physical foreground foreground barriers (e.g. from behind the White House or Tiananmen Gate).
- **Call-and-Response Staggering**: When the voiceover contrasts two concepts (e.g. *"interest alone costs more ... than the entire military"*), animate the first subject into the left frame immediately on the first noun, followed 1.0–1.5 seconds later by the second subject into the right frame.
- **Badge & Bubble Overshoot**: Metric pills and speech bubbles use elastic/overshoot easing (`back.out(1.4)`), expanding to ~108% before settling firmly into scale.

### 2.3 Secondary Environmental Motion
Every scene must maintain continuous micro-motion:
- Flags wave continuously (looping cloth wave).
- Ships rock gently in water (rotational ±0.8° oscillation).
- Ocean water surfaces surge and loop.
- Smoke and burning ember particles actively flicker on burning paper cutouts.

---

## 3. DOM & Stage Structure (`assets/starter-explainer-editorial.html`)

Every editorial explainer project starts from `starter-explainer-editorial.html`. The stage is strictly 1920×1080 scaled via:

```css
#stage {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 1920px;
  height: 1080px;
  transform: translate(-50%, -50%) scale(var(--s, 1));
  transform-origin: center center;
  overflow: hidden;
}
```

### Layer Hierarchy
```
#stage
├── #paper-grid (Paper texture + 40px grid pattern)
├── #camera-world (Transform rig containing all visual chapters)
│   ├── .chapter#chap-intro (Occluder building + popup figures)
│   ├── .chapter#chap-press (Tilted newspaper + highlighter wipe)
│   ├── .chapter#chap-sea (Halftone vessel + water surge + animated odometer)
│   ├── .chapter#chap-data (Floating chart card + 3D extruded map + comparison figures)
│   ├── .chapter#chap-diplomacy (Monument cutout + handshake + speech bubbles)
│   └── .chapter#chap-climax (Burning currency cutout + typewriter text + blinking cursor)
└── #global-progress-bar (Bottom 48px timeline tracker)
```

---

## 4. Reusable Component Recipes

### 4.1 Silhouette Offset Cutout
```html
<div class="figure-cutout figure-trump">
  <div class="silhouette-shadow"></div>
  <img src="assets/trump-cutout.png" alt="Trump" class="figure-img" />
</div>
```
```css
.figure-cutout {
  position: relative;
  display: inline-block;
}
.figure-cutout .figure-img {
  position: relative;
  display: block;
  filter: grayscale(100%) contrast(110%);
  z-index: 2;
}
.figure-cutout .silhouette-shadow {
  position: absolute;
  inset: 0;
  background-color: #CA4D2D;
  transform: translate(-18px, -14px);
  mask-image: var(--mask-url);
  -webkit-mask-image: var(--mask-url);
  mask-size: contain;
  mask-repeat: no-repeat;
  z-index: 1;
}
```

### 4.2 Animated Highlighter Marker
```html
<span class="hl-wrap">
  <span class="hl-marker"></span>
  <span class="hl-text">Empire Collapse</span>
</span>
```
```css
.hl-wrap { position: relative; display: inline-block; }
.hl-marker {
  position: absolute;
  inset: -2px -6px -2px -6px;
  background: #EFBC22;
  mix-blend-mode: multiply;
  transform-origin: left center;
  transform: scaleX(0); /* Animate to scaleX(1) via GSAP */
  border-radius: 3px;
  z-index: 1;
}
.hl-text { position: relative; z-index: 2; }
```

### 4.3 Animated Integer Counter (Odometer)
```javascript
function animateCounter(el, startVal, endVal, prefix = "$", suffix = "") {
  const obj = { val: startVal };
  return gsap.to(obj, {
    val: endVal,
    duration: 1.2,
    ease: "power2.out",
    onUpdate: () => {
      el.textContent = `${prefix}${Math.round(obj.val).toLocaleString()}${suffix}`;
    }
  });
}
```

### 4.4 Kinetic Typewriter with Blinking Cursor
```html
<div class="typewriter-block">
  <span class="tw-content" id="quote-line"></span><span class="tw-cursor">█</span>
</div>
```
```css
.typewriter-block {
  font-family: 'Courier New', Courier, monospace;
  font-size: 38px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #1A1A1A;
}
.tw-cursor {
  display: inline-block;
  color: #1A1A1A;
  animation: cursorBlink 0.65s steps(1) infinite;
}
@keyframes cursorBlink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

---

## 5. Sound Design Integration

Editorial Collage relies on physical, tactile sound effects mined automatically from the timeline:

| Visual Event | Tween / DOM Marker | SFX Trigger Tag | Family | Recommended Take |
|---|---|---|---|---|
| Newspaper slam | Newspaper scale & entrance | `{ data: "slam" }` | `impact` | `impact-heavy-01.wav` |
| Highlighter sweep | Marker `scaleX` wipe | `{ data: "draw" }` | `pen` | `pen-marker-scribble-01.wav` |
| Odometer number roll | Counter update start | `{ data: "counter" }` | `accent` | `counter-tick-mech-01.wav` |
| Comic speech bubble pop | Bubble scale overshoot | `{ data: "comic" }` | `ui` | `comic-pop-toon-04.wav` |
| 3D map landing | Map drop onto canvas | `{ data: "slam" }` | `impact` | `impact-heavy-01.wav` |
| Camera pan across data | Camera world translation | Camera rig tween | `whoosh` | `whoosh-camera-large-01.wav` |
| Typewriter sentence reveal | Word-by-word reveal | Flag `--word-clicks` | `camera` | `typewriter-classic-03.wav`, `typewriter-classic-04.wav` |
| Burning paper climax | Looping fire graphic | Scene entrance | `ambience` | `fire-crackle-paper-02.wav` |
| Ocean scene backdrop | Ship & sea stage | Scene entrance | `ambience` | `ocean-waves-ambient-02.wav` |
| Investigation drone bed | Entire composition | Audio mix stem | `ambience` | `tension-drone-sub-02.wav` |
