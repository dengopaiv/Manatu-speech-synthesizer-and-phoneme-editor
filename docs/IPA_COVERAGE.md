# IPA Coverage Matrix

Complete phoneme inventory for Manatu (131 phonemes total).

## Consonants (70)

### Pulmonic Consonants

Standard IPA chart layout: manner (rows) by place of articulation (columns). Voiceless/voiced pairs shown as vl./vd.

|  | Bilabial | Labiodental | Dental | Alveolar | Postalveolar | Retroflex | Palatal | Velar | Uvular | Pharyngeal | Glottal |
|--|----------|-------------|--------|----------|--------------|-----------|---------|-------|--------|------------|---------|
| **Stop** | p  b | | | t  d | | ʈ  ɖ | c  ɟ | k  g | q  ɢ | | ʔ |
| **Nasal** | m | ɱ | | n | | ɳ | ɲ | ŋ | ɴ | | |
| **Trill** | ʙ | | | r | | | | | ʀ | | |
| **Tap/Flap** | | ⱱ | | ɾ | | ɽ | | | | | |
| **Fricative** | ɸ  β | f  v | θ  ð | s  z | ʃ  ʒ | ʂ  ʐ | ç  ʝ | x  ɣ | χ  ʁ | ħ  ʕ | h  ɦ |
| **Alveolo-palatal fric.** | | | | | | | ɕ  ʑ | | | | |
| **Lateral fricative** | | | | ɬ  ɮ | | | | | | | |
| **Approximant** | | ʋ | | ɹ | | ɻ | j | ɰ | | | |
| **Lateral approximant** | | | | l | | ɭ | ʎ | ʟ | | | |

**Additional:** ʍ (voiceless labial-velar fricative), w (labial-velar approximant)

Note: ɡ (U+0261, IPA standard) is also mapped as an alias for g (U+0067).

### Affricates (6)

| Affricate | Components | Place | Voicing |
|-----------|------------|-------|---------|
| t͡ʃ | stop + fricative | Postalveolar | Voiceless |
| d͡ʒ | stop + fricative | Postalveolar | Voiced |
| t͡s | stop + fricative | Alveolar | Voiceless |
| d͡z | stop + fricative | Alveolar | Voiced |
| t͡ɬ | stop + lateral fricative | Alveolar | Voiceless |
| p͡f | stop + fricative | Labiodental | Voiceless |

Affricates use multi-phase envelopes: burst phase followed by sustained frication phase, with timing controlled per-phase.

### Ejectives (6)

Non-pulmonic consonants produced with a glottalic egressive airstream mechanism. The glottis closes, the larynx rises to compress trapped air, and oral release produces a sharp unaspirated burst.

| Symbol | Type | Place | Based on |
|--------|------|-------|----------|
| pʼ | Stop | Bilabial | p |
| tʼ | Stop | Alveolar | t |
| kʼ | Stop | Velar | k |
| qʼ | Stop | Uvular | q |
| t͡sʼ | Affricate | Alveolar | t͡s |
| t͡ʃʼ | Affricate | Postalveolar | t͡ʃ |

Acoustic characteristics vs. regular voiceless stops:
- No aspiration (glottal closure prevents airflow after burst)
- Sharper, more intense burst (compressed air behind closure)
- Longer closure (~18ms vs 12ms, glottal + oral closure builds pressure)
- Slight creaky voice onset (diplophonia from glottal opening)

The ejective diacritic ʼ (U+02BC) also works as a fallback modifier on any voiceless stop or affricate.

### Implosives (5)

Non-pulmonic consonants produced with a glottalic ingressive airstream mechanism. The larynx lowers during closure, maintaining voicing (voicebar) through the closure period and producing a weaker burst on release.

| Symbol | Type | Place | Based on | Languages |
|--------|------|-------|----------|-----------|
| ɓ | Stop | Bilabial | b | Hausa, Swahili, Sindhi |
| ɗ | Stop | Alveolar | d | Hausa, Swahili, Vietnamese |
| ɠ | Stop | Velar | g | Swahili, Kalenjin |
| ʄ | Stop | Palatal | ɟ | Sindhi, some Chadic |
| ʛ | Stop | Uvular | ɢ | Mam (rare) |

Acoustic characteristics vs. regular voiced stops:
- Voicing through closure (larynx descent maintains glottal vibration)
- Weaker burst (~80% of base, reduced oral pressure from ingressive airstream)
- Pressed/tense voice quality (lfRd=0.7, lower than modal 1.0)
- Slight creaky quality (diplophonia from glottal tension)
- More periodic voicing (less flutter from laryngeal tension)

## Vowels (34)

### Monophthongs

Standard IPA vowel chart: height (rows) by backness (columns). Rounded vowels shown after unrounded.

|  | Front | Central | Back |
|--|-------|---------|------|
| **Close** | i  y | ɨ  ʉ | ɯ  u |
| **Near-close** | ɪ  ʏ | | ʊ |
| **Close-mid** | e  ø | ɘ  ɵ | ɤ  o |
| **Open-mid** | ɛ  œ | ɜ  ɞ | ʌ  ɔ |
| **Near-open** | æ | ɐ | |
| **Open** | a  ɶ | | ɑ  ɒ |

In each cell, unrounded vowels are listed first, rounded second.

### R-colored Vowels (2)

| Symbol | Description |
|--------|-------------|
| ɝ | Stressed r-colored schwa (lowered F3, F4=2900 Hz) |
| ɚ | Unstressed r-colored schwa (lowered F3, F4=2900 Hz) |

### Nasalized Vowels (4)

| Symbol | Description | Language |
|--------|-------------|----------|
| ã | Nasalized open central | Portuguese, French |
| ɛ̃ | Nasalized open-mid front | French |
| ɔ̃ | Nasalized open-mid back | French |
| œ̃ | Nasalized open-mid front rounded | French |

Nasalized vowels use enhanced nasal pole (cfNP) and anti-resonance (cfN0) parameters with wider bandwidths.

## Diphthongs and Triphthongs (22)

### English (8)

| Symbol | Name | Components | Example |
|--------|------|------------|---------|
| aɪ | PRICE | a → ɪ | *price*, *high* |
| aʊ | MOUTH | a → ʊ | *mouth*, *now* |
| eɪ | FACE | e → ɪ | *face*, *day* |
| oʊ | GOAT | o → ʊ | *goat*, *show* |
| ɔɪ | CHOICE | ɔ → ɪ | *choice*, *boy* |
| ɪə | NEAR | ɪ → ə | *near*, *here* |
| eə | SQUARE | e → ə | *square*, *care* |
| ʊə | CURE | ʊ → ə | *cure*, *tour* |

### Lexical (3)

| Symbol | Components |
|--------|------------|
| ɑj | ɑ → i |
| ɑw | ɑ → u |
| ɔj | ɔ → i |

### Estonian (7)

| Symbol | Components | Example |
|--------|------------|---------|
| aj | a → i | *kai*, *lai* |
| ej | e → i | *hei*, *lei* |
| oj | o → i | *koi*, *loi* |
| uj | u → i | *tui*, *kui* |
| iʊ | i → ʊ | *liu*, *piu* |
| yj | y → i | *tüi*, *süi* |
| ɤj | ɤ → i | *õige*, *tõi* |

### Finnish (3)

| Symbol | Components | Example |
|--------|------------|---------|
| øy | ø → y | *löyly*, *pöytä* |
| uo | u → o | *suo*, *tuo* |
| yø | y → ø | *syö*, *lyö* |

### Livonian Triphthong (1)

| Symbol | Components | Example |
|--------|------------|---------|
| uoi | u → o → i | *kuoig* (fish) |

Diphthongs are expanded by the IPA parser into component vowels, with the synthesizer's Hermite smoothstep interpolation creating smooth glides between targets.

## Coverage Summary

| Category | Count |
|----------|-------|
| Monophthong vowels | 28 |
| R-colored vowels | 2 |
| Nasalized vowels | 4 |
| Diphthongs/triphthongs | 22 |
| Stops | 14 (incl. 1 alternate glyph) |
| Ejective stops | 4 |
| Fricatives | 27 |
| Affricates | 6 |
| Ejective affricates | 2 |
| Implosive stops | 5 |
| Nasals | 7 |
| Liquids & glides | 16 |
| **Total** | **137** |

## What's Missing (Phase 4 Targets)

The following IPA sound classes are not yet implemented:

- **Clicks** — ʘ, ǀ, ǃ, ǂ, ǁ (velaric ingressive mechanism)
- **Prenasalized stops** — ᵐb, ⁿd, ᵑɡ (common in Bantu and Oceanic languages)
- **Epiglottal consonants** — ʜ, ʢ, ʡ
