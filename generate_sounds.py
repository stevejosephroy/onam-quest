import wave, struct, math, random
import os

def save_wav(filename, samples, sample_rate=44100):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for s in samples:
            # clip and pack
            v = max(-32767, min(32767, int(s * 32767)))
            wav_file.writeframesraw(struct.pack('<h', v))

def gen_jump():
    samples = []
    # quick ascending slide
    for i in range(44100 // 4):  # 0.25 seconds
        t = i / 44100.0
        freq = 300 + 800 * t
        val = math.sin(2 * math.pi * freq * t)
        # envelope
        env = 1.0 - t * 4
        samples.append(val * env * 0.5)
    save_wav('assets/jump.wav', samples)

def gen_hit():
    samples = []
    for i in range(44100 // 3): # 0.33 seconds
        t = i / 44100.0
        val = random.uniform(-1.0, 1.0)
        env = max(0, 1.0 - t * 3)
        samples.append(val * env * 0.5)
    save_wav('assets/hit.wav', samples)

def gen_collect():
    samples = []
    for i in range(44100 // 5):
        t = i / 44100.0
        val = math.sin(2 * math.pi * 800 * t) * 0.5 + math.sin(2 * math.pi * 1200 * t) * 0.5
        env = max(0, 1.0 - t * 5)
        samples.append(val * env * 0.5)
    save_wav('assets/collect.wav', samples)

def gen_miss():
    samples = []
    for i in range(44100 // 2):
        t = i / 44100.0
        freq = 400 - 300 * t
        val = math.sin(2 * math.pi * freq * t)
        env = max(0, 1.0 - t * 2)
        samples.append(val * env * 0.5)
    save_wav('assets/miss.wav', samples)

if not os.path.exists('assets'):
    os.makedirs('assets')

gen_jump()
gen_hit()
gen_collect()
gen_miss()
print("Sounds generated!")
