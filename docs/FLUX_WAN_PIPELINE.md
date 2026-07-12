# Flux → Wan 2.2 Film Pipeline ("The PayLoad")

A production design for creating short films where **Flux generates the keyframes** (the starting pose, composition, and look of each shot) and **Wan 2.2 turns keyframe pairs into motion**. The goal: output that reads as *directed*, not generated.

---

## 1. Why this pipeline works

The two models split the job along their strengths:

| Stage | Model | Strength |
|---|---|---|
| Look development & keyframes | **Flux** (Flux Pro / Dev for hero stills, **Flux Kontext** for consistency edits) | Best-in-class still image quality, prompt adherence, and — via Kontext — identity-preserving edits of an existing image ("same character, new pose/angle/scene") |
| Motion | **Wan 2.2** (I2V and **FLF2V** — first-last-frame-to-video) | Treats supplied frames as hard boundary conditions inside the diffusion process, synthesizing coherent in-betweens rather than warping pixels |

The critical insight: **Wan 2.2 FLF2V respects your keyframes as ground truth.** If the first and last frames of a shot are beautiful, the shot is beautiful. All artistic control therefore concentrates in the Flux stage — which is exactly where a human curator can iterate cheaply (stills render in seconds; video in minutes/hours).

---

## 2. The handoff, precisely

The "handoff" is more than passing a PNG. Five things must survive the transfer:

1. **Pixel-exact framing** — generate Flux keyframes at (or crop to) the exact aspect ratio and resolution Wan will render (e.g. 1280×720 or 832×480 for 14B). Mismatched aspect ratios cause warping at the boundaries.
2. **World consistency between frame pairs** — the first and last frame of a shot must share color grade, light direction, lens character, and film grain. If they look like two photo shoots, Wan hallucinates a "transition" instead of motion. Flux Kontext is the tool here: derive the last frame *from* the first frame ("same scene, character now standing at the window"), never from scratch.
3. **Plausible motion distance** — the two frames must be reachable within the clip length (≤ 5–8 s; beyond that FLF2V reliability drops). A character can turn their head in 3 seconds; they cannot cross a city.
4. **The motion prompt** — Wan's prompt should describe *what happens between* the frames (movement, camera, pacing), not what's in them. The images already define the "what."
5. **Seed/settings continuity** — fixed seeds for Flux keyframe families; consistent sampler/CFG for Wan across shots in a scene, so texture and motion character don't shift shot-to-shot.

---

## 3. The film creation process (six phases)

### Phase 0 — Script & shot list
Standard pre-production, but every shot gets machine-readable metadata:

```yaml
shot: 12
scene: 3
duration_s: 5
type: FLF2V          # or I2V (single keyframe, free motion) or T2V (rare)
first_frame: shot12_A.png
last_frame:  shot12_B.png
motion_prompt: "She turns from the window toward camera; slow dolly-in; curtains drift in the breeze; soft handheld sway"
camera: "35mm, slow dolly-in"
lighting_ref: scene3_lut
```

### Phase 1 — Look development (Flux)
Before any shot work, lock the film's visual identity:
- Generate a **style bible**: 6–12 hero frames defining palette, grain, lens, era, mood. Curate hard — reject anything "AI-pretty" but off-brand.
- Build **character sheets** with Flux + Kontext: front/profile/¾ views, key costumes, neutral background. These become the reference images for every subsequent Kontext edit.
- Write a reusable **style suffix** appended to every keyframe prompt (film stock, grade, grain, lens family) so the whole film shares one look.

**Flux prompting rules (cinematographer's language, not adjectives):**
- Front-load the subject and action; Flux weights the start of the prompt heaviest.
- Specify light as behavior: "soft morning light from the left, long gentle shadows" — never "beautiful lighting."
- Specify camera physically: body/lens/aperture ("85mm f/1.8, shallow depth of field, background compression").
- One primary style. Style-stuffing ("cinematic, oil painting, 3D render") produces mud.

### Phase 2 — Keyframe generation (Flux → the shot's first frame)
For each shot:
1. Compose the **first frame** using the style suffix + character references. Iterate with the curator until it's a frame you'd hang on a wall — this frame *is* the shot's look.
2. Derive the **last frame** with **Flux Kontext** from the first frame: "same scene, same lighting, character now ___" at strength ~0.7–0.85, fixed seed. This guarantees the same-world requirement.
3. For shots continuing from a previous shot (match cuts, continuous action): extract the previous shot's final rendered frame and use it (or a Kontext-cleaned version of it) as this shot's first frame.

**Curation gate:** a human approves every keyframe pair side-by-side before video generation. Check: identity match, light direction match, grade match, reachable motion.

### Phase 3 — Motion (Wan 2.2)
- **FLF2V** for storyboarded/controlled shots: reveals, camera moves with a known end composition, action beats, match cuts.
- **I2V** (first frame only) for shots where organic, discoverable motion is desirable: ambience, weather, crowd life, performance moments.
- Motion prompts: 80–120 words, movement-and-camera only. Use Wan's camera vocabulary explicitly: *dolly in/out, pan, tilt, tracking, orbital arc, crane, whip pan, fixed lens* (for locked-off shots).
- Clip length 3–6 s per generation. Longer beats = chain multiple FLF2V segments through shared intermediate keyframes (shot 12a's last frame = shot 12b's first frame).
- Render draft passes on the 5B model for pacing/blocking review; final passes on 14B.

### Phase 4 — Anti-drift & repair
Known failure modes and their fixes:
- **Identity/color drift across chained clips** ("copy of a copy"): never chain more than 2–3 segments off rendered frames. Re-anchor by generating a *fresh* Flux Kontext keyframe from the character sheet, matched to the drifted frame's composition, and continue from that.
- **Grade drift between shots**: pick one hero clip per scene as the color reference; conform every other clip to it in DaVinci Resolve (waveform-matched blacks/whites, skin tones aligned on vectorscope).
- **Boundary "pop"** at the last frame: if the final frames snap to the target, retime the last ~8 frames or regenerate with a slightly longer duration.
- **Failed shots**: fix the *keyframes*, not the video prompt, first. 80% of bad Wan output traces to a keyframe problem.

### Phase 5 — Post
Upscale (e.g. Topaz / SeedVR2), interpolate to 24 fps if generated lower, unified grain pass (one grain layer over everything hides residual texture mismatch), sound design, edit. The unified grade + grain pass is what makes curators stop seeing "AI clips" and start seeing *a film*.

---

## 4. Shot-type playbook

| Shot need | Recipe |
|---|---|
| Establishing shot | Flux wide keyframe → Wan I2V, "slow push-in, fixed lens, atmospheric drift" |
| Dialogue two-shot | Keyframe pair with tiny pose delta → FLF2V, "subtle head turns, breathing, micro camera sway" |
| Action beat | Kontext-derived start/end poses → FLF2V, explicit motion path in prompt |
| Reveal / match cut | Last frame designed first (the reveal), first frame derived backward via Kontext → FLF2V |
| Continuous long take | Chain FLF2V segments through shared keyframes, re-anchor identity every 2 segments |
| Ambient insert | Single Flux keyframe → I2V, motion prompt only about environment |

---

## 5. Operating principles

1. **All taste lives in stills.** Iterate ruthlessly where iteration is cheap (Flux), commit only approved frames to expensive motion (Wan).
2. **Never generate a last frame from scratch.** Always derive it (Kontext) from the first frame or a rendered frame.
3. **Prompts describe physics and optics,** not quality adjectives — for both models.
4. **The keyframe pair review is the quality gate.** Nothing renders to video without it.
5. **Drift is fought at the source** (fresh Kontext anchors) and in post (single-reference grade), never by re-prompting harder.

---

## Sources

- [Wan 2.2 14B FLF2V — official ComfyUI workflow](https://comfy.org/workflows/video_wan2_2_14B_flf2v-7016f027bcf1/)
- [WAN 2.2 First-Last Frame Video Generation in ComfyUI — Next Diffusion](https://www.nextdiffusion.ai/tutorials/wan-22-first-last-frame-video-generation-in-comfyui)
- [Wan 2.2 FLF2V: Two-Frame Interpolation — RunComfy](https://www.runcomfy.com/models/community/wan-2-2/first-last-frame)
- [Wan 2.2 First Last Frame Video — Stable Diffusion Art](https://stable-diffusion-art.com/wan-2-2-first-last-frame-video/)
- [FLUX.1 Kontext: consistent characters without fine-tuning — Together AI](https://www.together.ai/blog/flux-1-kontext)
- [Flux Kontext character consistency for video — FluxNote](https://fluxnote.io/blog/flux-kontext-image-guide-2026)
- [How to Use FLUX AI: Prompts, Settings & Tips — fal](https://fal.ai/learn/tools/how-to-use-flux)
- [Wan 2.2 prompt guide — instasd](https://www.instasd.com/post/wan2-2-whats-new-and-how-to-write-killer-prompts)
- [Wan2.2 cinematic prompting & camera control](https://wan2.video/wan2.2-guide)
- [DaVinci Resolve color grading for AI footage — invideo](https://invideo.io/blog/davinci-color-grading-ai/)
- [Fixing AI video drift — Kling](https://kling.ai/blog/fix-ai-video-drift-consistency-guide)
