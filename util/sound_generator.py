# import numpy as np
# import wave
# import os
#
# # D Kurd 9 handpan layout from image:
# # Center: D4
# # Ring (clockwise from top): A3, G4, E4, C5, A4, Bb4, D5, F4
# NOTE_FREQUENCIES = {
#     'A3': 220.00,
#     'G4': 392.00,
#     'E4': 329.63,
#     'C5': 523.25,
#     'A4': 440.00,
#     'Bb4': 466.16,
#     'D5': 587.33,
#     'F4': 349.23,
#     'D4': 293.66,
# }
#
# def generate_sounds(output_dir='../assets/sounds', duration=1.0, sample_rate=44100):
#     """
#     Generate simple sine-wave WAV files for each note in NOTE_FREQUENCIES.
#     """
#     os.makedirs(output_dir, exist_ok=True)
#     for note, freq in NOTE_FREQUENCIES.items():
#         wav_path = os.path.join(output_dir, f"{note}.wav")
#         print(f"Generating {wav_path} at {freq} Hz")
#         t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
#         waveform = 0.5 * np.sin(2 * np.pi * freq * t)
#         fade_len = int(0.01 * sample_rate)
#         envelope = np.ones_like(waveform)
#         envelope[:fade_len] = np.linspace(0, 1, fade_len)
#         envelope[-fade_len:] = np.linspace(1, 0, fade_len)
#         waveform *= envelope
#         pcm_wave = np.int16(waveform * 32767)
#         with wave.open(wav_path, 'wb') as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(sample_rate)
#             wf.writeframes(pcm_wave.tobytes())
#
# if __name__ == '__main__':
#     generate_sounds()

import os
import numpy as np
from scipy.io import wavfile

NOTES_FREQUENCIES = {
'DD': 293.66,
'A': 220.00,
'E': 392.00,
'a': 329.63,
'D': 523.25,
'C': 440.00,
'Bb': 466.16,
'F': 587.33,
'G': 349.23
}
# NOTES_FREQUENCIES = {
#     'D4': 293.66,  # Center ding
#     'A3': 220.00,
#     'G4': 392.00,
#     'E4': 329.63,
#     'C5': 523.25,
#     'A4': 440.00,
#     'Bb4': 466.16,
#     'D5': 587.33,
#     'F4': 349.23,
# }
SAMPLE_RATE = 44100
DURATION = 2 # Saniye cinsinden her bir nota sesi için varsayılan süre

def generate_sine_wave(frequency, duration, sample_rate=SAMPLE_RATE, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return (wave * (2**15 - 1) / np.max(np.abs(wave))).astype(np.int16) # 16-bit PCM'e normalize et

def generate_sounds(output_dir='assets/sounds', notes=None):
    if notes is None:
            notes = NOTES_FREQUENCIES.keys()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for note_name in notes:
        frequency = NOTES_FREQUENCIES.get(note_name)
        if frequency:
            wave_data = generate_sine_wave(frequency, DURATION)
            wav_path = os.path.join(output_dir, f"{note_name}.wav")
            wavfile.write(wav_path, SAMPLE_RATE, wave_data)
            print(f"Generated {wav_path}")

# Eğer bu dosya doğrudan çalıştırılırsa sesleri üretmek için:
if __name__ == '__main__':
    assets_sounds_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')
    generate_sounds(output_dir=assets_sounds_dir)