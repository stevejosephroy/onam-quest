import wave, struct, math, random

def generate_creepy_bgm():
    sample_rate = 44100
    duration = 4.0 # 4 seconds loop
    samples = [0.0] * int(sample_rate * duration)
    
    # Low dissonant drone (Pathalam rumble)
    freq1 = 55.0 # Low A
    freq2 = 58.27 # Low Bb (minor second clash)
    
    for s in range(len(samples)):
        t = s / sample_rate
        # Sub-bass rumble
        rumble = math.sin(2 * math.pi * freq1 * t) * 0.4
        rumble += math.sin(2 * math.pi * freq2 * t) * 0.4
        
        # Add a slow pulsing LFO to the volume
        lfo = (math.sin(2 * math.pi * 0.5 * t) + 1) / 2
        rumble *= (0.5 + 0.5 * lfo)
        
        # Add some high pitched random noise sweeps occasionally
        noise = random.uniform(-1, 1) * 0.05
        
        samples[s] = rumble + noise

    # Add a discordant bell every 2 seconds
    bell_freqs = [440.0, 622.25] # A and D# (Tritone / Devil's interval)
    for i in range(2):
        start_sample = int((i * 2.0) * sample_rate)
        for s in range(start_sample, len(samples)):
            t = (s - start_sample) / sample_rate
            env = math.exp(-2.0 * t) # Quick decay
            if env < 0.01:
                break
            
            bell = math.sin(2 * math.pi * bell_freqs[0] * t) * 0.3
            bell += math.sin(2 * math.pi * bell_freqs[1] * t) * 0.3
            samples[s] += bell * env

    # Save to wav
    with wave.open('assets/bgm_creepy.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for s_val in samples:
            # clip and pack
            v = max(-32767, min(32767, int(s_val * 32767)))
            wav_file.writeframesraw(struct.pack('<h', v))

generate_creepy_bgm()
print("Creepy BGM generated!")
