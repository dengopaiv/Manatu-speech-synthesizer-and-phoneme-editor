# analyze_formants.praat - Outputs formant values as text
# Usage: praat --run analyze_formants.praat input.wav
# Accessible output for screen readers

form Analyze formants
    text input_file test.wav
endform

Read from file: input_file$
sound = selected("Sound")

# Extract formants (Burg method)
# Parameters: time step (0=auto), max formants (5), max freq (5500 Hz for male voice), window (25ms), pre-emphasis (50 Hz)
To Formant (burg): 0, 5, 5500, 0.025, 50
formant = selected("Formant")

# Get values at midpoint of sound (most stable region)
duration = Get total duration
midpoint = duration / 2

f1 = Get value at time: 1, midpoint, "hertz", "Linear"
f2 = Get value at time: 2, midpoint, "hertz", "Linear"
f3 = Get value at time: 3, midpoint, "hertz", "Linear"
f4 = Get value at time: 4, midpoint, "hertz", "Linear"
b1 = Get bandwidth at time: 1, midpoint, "hertz", "Linear"
b2 = Get bandwidth at time: 2, midpoint, "hertz", "Linear"
b3 = Get bandwidth at time: 3, midpoint, "hertz", "Linear"
b4 = Get bandwidth at time: 4, midpoint, "hertz", "Linear"

# Output as plain text (screen-reader friendly)
writeInfoLine: "FORMANT ANALYSIS RESULTS"
appendInfoLine: "========================"
appendInfoLine: "File: ", input_file$
appendInfoLine: "Duration: ", fixed$(duration * 1000, 0), " ms"
appendInfoLine: ""
appendInfoLine: "MEASURED FORMANTS:"
appendInfoLine: "  F1: ", fixed$(f1, 0), " Hz (bandwidth: ", fixed$(b1, 0), " Hz)"
appendInfoLine: "  F2: ", fixed$(f2, 0), " Hz (bandwidth: ", fixed$(b2, 0), " Hz)"
appendInfoLine: "  F3: ", fixed$(f3, 0), " Hz (bandwidth: ", fixed$(b3, 0), " Hz)"
appendInfoLine: "  F4: ", fixed$(f4, 0), " Hz (bandwidth: ", fixed$(b4, 0), " Hz)"
appendInfoLine: ""
appendInfoLine: "REFERENCE TARGETS (Adult Male):"
appendInfoLine: "  i: F1=270-310, F2=2290-2790, F3=3010-3310"
appendInfoLine: "  e: F1=400-480, F2=2020-2290, F3=2600-2700"
appendInfoLine: "  a: F1=730-850, F2=1090-1350, F3=2440-2600"
appendInfoLine: "  o: F1=450-500, F2=830-920, F3=2380-2500"
appendInfoLine: "  u: F1=300-340, F2=870-1020, F3=2240-2380"

# Clean up
selectObject: sound
Remove
selectObject: formant
Remove
