import speechPlayer

# Test with different fade durations
for fade_ms in [0, 5, 10, 20, 50]:
    sp = speechPlayer.SpeechPlayer(44100)

    burst_frame = speechPlayer.Frame()
    for name, _ in burst_frame._fields_:
        setattr(burst_frame, name, 0.0)
    burst_frame.voicePitch = 120
    burst_frame.endVoicePitch = 120
    burst_frame.outputGain = 2.0
    burst_frame.preFormantGain = 1.0
    burst_frame.burstAmplitude = 0.8
    burst_frame.burstDuration = 0.3
    burst_frame.parallelBypass = 1.0

    sp.queueFrame(burst_frame, 100, fade_ms)
    sp.queueFrame(None, 50, 10)

    all_samples = []
    for _ in range(10):
        samples = sp.synthesize(4096)
        if samples and samples.length > 0:
            all_samples.extend(samples[:samples.length])
        else:
            break

    # Find the overall max
    overall_max = max(abs(s) for s in all_samples) if all_samples else 0

    # Look at different time regions
    fade_samples = int(fade_ms * 44.1)
    print(f"Fade {fade_ms:2d}ms: total_samples={len(all_samples)}, overall_max={overall_max}")
