# Manatu Vision

## Mission Statement

Build a research-grounded, academically-accurate Klatt speech synthesizer that **exceeds the quality of Dectalk and Eloquence** while providing **complete IPA phoneme coverage** - delivered as an NVDA addon for blind users.

## Core Philosophy

**Research enables production quality.** The NVDA addon is the end goal, but it's only achievable through deep understanding of synthesis principles. Tools like the phoneme editor aren't optional extras - they're essential for achieving quality.

---

## End Goals

### 1. Synthesis Quality
- **Exceed classics**: Sound better than Dectalk/Eloquence using modern KLSYN88 improvements
- **Academic accuracy**: Parameters grounded in published phonetics research (Klatt, Stevens, Hillenbrand)
- **Natural transitions**: Coarticulation, S-curve smoothing, proper formant dynamics

### 2. Phoneme Coverage
- **Complete IPA**: All human speech sounds, not just English
- **Priority order**:
  1. Core synthesis engine working correctly
  2. Vowels (complete, high-quality)
  3. Consonants: frequent → rare (stops, fricatives, nasals, liquids → retroflexes → ejectives, implosives → clicks)

### 3. Deliverable
- **Primary**: Production-ready NVDA addon that blind users can rely on daily
- **Supporting**: Research/testing tools (phoneme editor, analyzers) that enable quality development

---

## Development Phases

### Phase 0: Foundation — Done
- Core synthesis engine (KLSYN88-based)
- Basic phoneme data structure
- Phoneme editor tool
- Parameter infrastructure (spectral tilt, flutter, LF model, etc.)

### Phase 1: Vowels — Done
- All IPA vowels with accurate formants (F1-F6)
- Voice quality consistency across vowels
- Vowel stability (no warbling/drift)
- Diphthong transitions

### Phase 2: Common Consonants — Done
- Stops (p, b, t, d, k, g) with proper bursts
- Fricatives (f, v, s, z, ʃ, ʒ, θ, ð, h) with place-specific spectra
- Nasals (m, n, ŋ)
- Liquids and glides (l, r, w, j)
- Affricates (tʃ, dʒ)

### Phase 3: Extended Consonants — Done
- Retroflexes (ʈ, ɖ, ʂ, ʐ, ɳ, ɭ)
- Palatals (c, ɟ, ç, ʝ, ɲ, ʎ), uvulars (q, ɢ, χ, ʁ, ɴ, ʀ), pharyngeals (ħ, ʕ)
- Voiced/voiceless pairs for all places
- Trills (r, ʀ, ʙ), bilabial fricatives (ɸ, β), extended approximants (ʋ, ɻ, ɰ)
- Lateral fricatives (ɬ, ɮ), velar fricatives (x, ɣ), additional affricates (t͡s, d͡z, t͡ɬ, p͡f)

### Phase 4: Non-Pulmonic & Exotic (Next)
- Ejectives
- Implosives
- Clicks
- Prenasalized stops

### Phase 5: Polish & Integration
- Prosody refinement (pitch, timing, stress)
- NVDA addon packaging and testing
- Documentation for users

---

## Success Criteria

| Aspect | Minimum | Target |
|--------|---------|--------|
| Vowel accuracy | Within 15% of published formants | Within 5% |
| Consonant coverage | English phonemes | Full IPA |
| Transitions | No audible glitches | Natural coarticulation |
| Responsiveness | Matches eSpeak | Faster than eSpeak |
| Stability | No crashes | Production-ready |

---

## Guiding Principles

1. **Research before implementation**: Understand the acoustic science before coding
2. **Evidence-based tuning**: Use published formant values, not trial-and-error
3. **Tools are investment**: Time spent on editors/analyzers pays off in quality
4. **Quality over speed**: Get sounds right before adding more sounds
5. **Document everything**: Future-you needs to understand current-you's decisions

---

## Key References

- Klatt 1980: "Software for a cascade/parallel formant synthesizer"
- Klatt & Klatt 1990: "Analysis, synthesis, and perception of voice quality variations"
- Stevens 1998: "Acoustic Phonetics"
- Hillenbrand et al. 1995: Vowel formant measurements
- Agrawal & Stevens 1992: Retroflex consonant parameters
