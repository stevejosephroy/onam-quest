import wave, struct, math

def generate_bgm():
    sample_rate = 44100
    duration = 4.0 # 4 seconds loop
    samples = [0.0] * int(sample_rate * duration)
    
    # Mohanam scale frequencies (C, D, E, G, A) - traditional Kerala vibe
    notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]
    
    # Pattern of notes (arpeggio)
    sequence = [0, 2, 4, 3, 5, 4, 2, 1, 0, 3, 2, 4, 6, 5, 3, 2]
    note_duration = duration / len(sequence)
    
    for i, note_idx in enumerate(sequence):
        freq = notes[note_idx]
        start_sample = int(i * note_duration * sample_rate)
        end_sample = int((i + 1) * note_duration * sample_rate)
        
        for s in range(start_sample, end_sample):
            t = (s - start_sample) / sample_rate
            
            # Simple additive synthesis (sine + triangle) for a soft bell/flute sound
            val = math.sin(2 * math.pi * freq * t) * 0.6
            val += math.sin(2 * math.pi * freq * 2 * t) * 0.2
            
            # Envelope (soft attack, long release)
            env = math.exp(-3 * t)
            
            samples[s] += val * env * 0.3
            
    # Add a soft drone (sruti) in the background
    drone_freq = notes[0] / 2 # Low C
    for s in range(len(samples)):
        t = s / sample_rate
        drone = math.sin(2 * math.pi * drone_freq * t) * 0.15
        drone += math.sin(2 * math.pi * drone_freq * 1.5 * t) * 0.05
        samples[s] += drone
            
    # Save to wav
    with wave.open('assets/bgm.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for s_val in samples:
            # clip and pack
            v = max(-32767, min(32767, int(s_val * 32767)))
            wav_file.writeframesraw(struct.pack('<h', v))

generate_bgm()
print("BGM generated!")
