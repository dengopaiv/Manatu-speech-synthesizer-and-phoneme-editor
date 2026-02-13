# IPA Coverage Matrix

Complete phoneme inventory for Manatu (152 explicit phonemes + 9 diacritic modifiers).

## Consonants (85)

### Pulmonic Consonants

Standard IPA chart layout: manner (rows) by place of articulation (columns). Voiceless/voiced pairs shown as vl./vd.

|  | Bilabial | Labiodental | Dental | Alveolar | Postalveolar | Retroflex | Palatal | Velar | Uvular | Pharyngeal | Epiglottal | Glottal |
|--|----------|-------------|--------|----------|--------------|-----------|---------|-------|--------|------------|------------|---------|
| **Stop** | p  b | | | t  d | | ʈ  ɖ | c  ɟ | k  g | q  ɢ | | ʡ | ʔ |
| **Nasal** | m | ɱ | | n | | ɳ | ɲ | ŋ | ɴ | | | |
| **Trill** | ʙ | | | r | | | | | ʀ | | | |
| **Tap/Flap** | | ⱱ | | ɾ | | ɽ | | | | | | |
| **Fricative** | ɸ  β | f  v | θ  ð | s  z | ʃ  ʒ | ʂ  ʐ | ç  ʝ | x  ɣ | χ  ʁ | ħ  ʕ | ʜ  ʢ | h  ɦ |
| **Alveolo-palatal fric.** | | | | | | | ɕ  ʑ | | | | | |
| **Lateral fricative** | | | | ɬ  ɮ | | | | | | | | |
| **Approximant** | | ʋ | | ɹ | | ɻ | j | ɰ | | | | |
| **Lateral approximant** | | | | l  ɫ | | ɭ | ʎ | ʟ | | | | |

**Additional:** ʍ (voiceless labial-velar fricative), w (labial-velar approximant)

Note: ɡ (U+0261, IPA standard) is also mapped as an alias for g (U+0067). ɫ is the velarized (dark) lateral approximant.

### Affricates (9)

| Affricate | Components | Place | Voicing |
|-----------|------------|-------|---------|
| t͡ʃ | stop + fricative | Postalveolar | Voiceless |
| d͡ʒ | stop + fricative | Postalveolar | Voiced |
| t͡s | stop + fricative | Alveolar | Voiceless |
| d͡z | stop + fricative | Alveolar | Voiced |
| t͡ɬ | stop + lateral fricative | Alveolar | Voiceless |
| d͡ɮ | stop + lateral fricative | Alveolar | Voiced |
| t͡ɕ | stop + fricative | Alveolo-palatal | Voiceless |
| d͡ʑ | stop + fricative | Alveolo-palatal | Voiced |
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

### Prenasalized Stops (3)

Prenasalized stops begin with a nasal murmur phase before a voiced stop release. Common in Bantu (Swahili, Zulu) and Oceanic (Fijian) languages. Implemented using the multi-phase system (same as affricates).

| Symbol | Type | Place | Based on | Languages |
|--------|------|-------|----------|-----------|
| ᵐb | Prenasalized stop | Bilabial | m + b | Swahili, Fijian |
| ⁿd | Prenasalized stop | Alveolar | n + d | Swahili, Fijian |
| ᵑɡ | Prenasalized stop | Velar | ŋ + g | Swahili, Fijian |

Acoustic characteristics:
- Phase 1: ~60ms nasal murmur with nasal pole/zero active (caNP=1)
- Phase 2: ~8ms voiced stop release with burst energy
- Voicing maintained throughout both phases
- Superscript nasal prefix (ᵐ, ⁿ, ᵑ) parsed via 2-character longest match

Note: ᵑɡ (with IPA ɡ U+0261) and ᵑg (with ASCII g U+0067) are both supported.

### Epiglottal Consonants (3)

Rare sounds produced at the epiglottis, further back than pharyngeals. Found in some Caucasian languages (Agul) and East African languages (Dahalo).

| Symbol | Type | Place | Based on | Languages |
|--------|------|-------|----------|-----------|
| ʜ | Voiceless fricative | Epiglottal | ħ | Agul, some Caucasian |
| ʢ | Voiced fricative | Epiglottal | ʕ | Agul, some Caucasian |
| ʡ | Stop | Epiglottal | ʔ | Dahalo, some Caucasian |

Acoustic characteristics vs. pharyngeal neighbors:
- Higher F1 than pharyngeals (epiglottal constriction raises F1 further)
- Lower F2 (more posterior articulation)
- Stronger aspiration/breathiness (ʜ: spectralTilt=14 vs ħ=12)
- More creaky voice quality (ʢ: diplophonia=0.2 vs ʕ=0.15)

### Click Consonants (5)

Clicks are produced with a velaric ingressive airstream mechanism. The current engine approximates them using the burst generator with short, sharp transients — recognizable if not acoustically perfect.

| Symbol | Name | Burst Freq | Character | Languages |
|--------|------|-----------|-----------|-----------|
| ʘ | Bilabial click | 600 Hz | Diffuse pop, like lip smack | Zulu, !Xoo |
| ǀ | Dental click | 4000 Hz | Sharp "tsk" | Zulu, Xhosa |
| ǃ | Postalveolar click | 2500 Hz | Loud "cluck" | Zulu, !Xoo |
| ǂ | Palatal click | 3500 Hz | Softer "clop" | !Xoo, Sandawe |
| ǁ | Lateral click | 5000 Hz | Lateral "tchk" | Zulu, Xhosa |

Each click is implemented as a 2-phase stop:
- Phase 1 (click burst): 4ms, high-amplitude burst with characteristic spectral shape
- Phase 2 (velar release): 6ms, lower burst mimicking the velar back-release

## Diacritic Modifiers (9)

Diacritics modify base phonemes to create hundreds of additional combinations. Pre-computed entries (e.g. ɛ̃ in nasalized vowels) are matched first; the generic handler fires for all other combinations.

### Superscript Modifiers (Secondary Articulation)

| Modifier | Name | Effect | Parameter Changes |
|----------|------|--------|-------------------|
| ʰ | Aspiration | Post-stop aspiration | Inserts /h/ phoneme after stop |
| ʼ | Ejective | Glottalic egressive | Sharper burst, no aspiration, diplophonia |
| ʷ | Labialization | Lower F2 toward lip rounding | cf2/pf2 blend 25% toward 700 Hz |
| ʲ | Palatalization | Raise F2 toward palatal | cf2/pf2 blend 30% toward 2300 Hz |
| ˠ | Velarization | Lower F2 toward velar | cf2/pf2 blend 25% toward 1200 Hz |
| ˤ | Pharyngealization | Raise F1, lower F2 | cf1/pf1 blend 30% toward 700 Hz, cf2/pf2 blend 25% toward 1000 Hz |

### Combining Diacritics (Voice Quality / Manner)

| Diacritic | Unicode | Name | Effect | Parameter Changes |
|-----------|---------|------|--------|-------------------|
| ̥ | U+0325 | Voiceless | Remove voicing | voiceAmplitude=0, lfRd=0, _isVoiced=False |
| ̤ | U+0324 | Breathy | Breathy voice | lfRd=max(lfRd, 2.5), spectralTilt += 8 |
| ̰ | U+0330 | Creaky | Creaky voice | lfRd=min(lfRd, 0.5), diplophonia += 0.3 |
| ̃ | U+0303 | Nasalized | Add nasal resonance | caNP=0.5, cfNP=270 |
| ̩ | U+0329 | Syllabic | Consonant as nucleus | _isSyllabic=True |

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
| Stops | 15 (incl. 1 alternate glyph) |
| Ejective stops | 4 |
| Fricatives | 29 |
| Affricates | 9 |
| Ejective affricates | 2 |
| Implosive stops | 5 |
| Prenasalized stops | 3 (incl. 1 alternate glyph) |
| Epiglottal consonants | 3 |
| Click consonants | 5 |
| Nasals | 7 |
| Liquids & glides | 17 |
| Diacritic modifiers | 9 |
| **Explicit phonemes** | **152** |
| **Effective combinations** | **500+** (diacritics on any base) |
