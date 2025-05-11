import streamlit as st
import os
import json
import math
import io
import wave
import base64
import json as pyjson
import util.sound_generator as sg
import streamlit.components.v1 as components

st.set_page_config(page_title="D Kurd 9 Handpan Player", layout="wide")


def load_songs_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('songs', [])
    except Exception as e:
        st.error(f"Şarkı dosyası yüklenirken hata: {e}")
        return []


def combine_wav_io(sequence, sounds_dir):
    sample_rate = sample_width = n_channels = None
    frames = []
    for note, dur in sequence:
        wav_path = os.path.join(sounds_dir, f"{note}.wav")
        if not os.path.exists(wav_path):
            st.error(f"Ses dosyası bulunamadı: {note}.wav")
            return None
        with wave.open(wav_path, 'rb') as wf:
            if sample_rate is None:
                sample_rate = wf.getframerate()
                sample_width = wf.getsampwidth()
                n_channels = wf.getnchannels()
            # Read full sample and pad silence if shorter
            raw = wf.readframes(int(dur * sample_rate))
            frames.append(raw)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf_out:
        wf_out.setnchannels(n_channels)
        wf_out.setsampwidth(sample_width)
        wf_out.setframerate(sample_rate)
        wf_out.writeframes(b"".join(frames))
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    songs = load_songs_json(os.path.join(base_dir, 'assets', 'songs.json'))
    if not songs:
        st.info("assets/songs.json dosyasında şarkı bulunamadı.")
        return

    st.title("🎶 D Kurd 9 Handpan Player")
    song_map = {s['name']: s['sequence'] for s in songs}

    col1, col2 = st.columns([3,1])
    with col1:
        choice = st.selectbox("Select song", list(song_map.keys()))
    with col2:
        speed = st.slider("Speed (x)", 0.5, 2.0, 1.0, 0.1)

    seq_orig = song_map[choice]
    sequence = [[note, dur/speed] for note, dur in seq_orig]

    if st.button("🎵 Prepare and Play"):
        sounds_dir = os.path.join(base_dir, 'assets', 'sounds')
        if sg and (not os.path.isdir(sounds_dir) or not os.listdir(sounds_dir)):
            with st.spinner("Nota sesleri üretiliyor..."):
                all_notes = {n for song in songs for n,_ in song['sequence']}
                sg.generate_sounds(output_dir=sounds_dir, notes=list(all_notes))
        elif not sg:
            st.warning("Ses üretici modülü bulunamadı; hazır WAV dosyalarını kullanın.")

        # NOTE POSITIONS
        center_x, center_y = 300, 250
        radius = 180
        handpan_notes = ['DD','A','Bb','D','F','a','G','E','C']
        # Order such that A3 & Bb4 at bottom side-by-side
        ring_notes = [n for n in handpan_notes if n!='DD']
        angle_step = 360 / len(ring_notes)
        half = angle_step/2
        positions = {'DD':(center_x,center_y)}
        # start angle at bottom-ish: 90° - half
        start_angle = 90 - half
        for i,note in enumerate(ring_notes):
            ang = math.radians(start_angle + angle_step*i)
            positions[note] = (center_x + radius*math.cos(ang), center_y + radius*math.sin(ang))

        # Build schedule starts
        current = 0.0
        schedule = []
        for note,dur in sequence:
            schedule.append({'note':note,'start':current})
            current += dur

        # JSON for JS
        pos_js = pyjson.dumps([{'note':n,'x':positions[n][0],'y':positions[n][1]} for n in handpan_notes])
        sched_js = pyjson.dumps(schedule)
        audio_b64 = combine_wav_io(sequence, sounds_dir)
        if not audio_b64:
            return

        html = f"""
        <div style='text-align:center'>
          <canvas id='hpCanvas' width='600' height='500'></canvas><br>
          <audio id='hpAudio' controls style='width:100%'></audio>
        </div>
        <script>
          const positions = {pos_js};
          const schedule = {sched_js};
          const audio = document.getElementById('hpAudio');
          const canvas = document.getElementById('hpCanvas');
          const ctx = canvas.getContext('2d');
          audio.src = 'data:audio/wav;base64,{audio_b64}';

          const HIT_WINDOW = 0.1;
          let hitEnd = Array(schedule.length).fill(0);
          let processed = Array(schedule.length).fill(false);

          function updateHits() {{
            const t = audio.currentTime;
            for(let i=0;i<schedule.length;i++){{
              const item=schedule[i];
              if(!processed[i] && t>=item.start){{ processed[i]=true; hitEnd[i]=t+HIT_WINDOW; }}
              if(t<item.start){{ processed[i]=false; hitEnd[i]=0; }}
            }}
          }}

          function draw() {{
            const t = audio.currentTime;
            ctx.fillStyle='rgb(40,42,54)'; ctx.fillRect(0,0,600,500);
            positions.forEach(p=>{{
              ctx.beginPath();
              ctx.arc(p.x,p.y,35,0,2*Math.PI);
              let col='rgb(150,150,150)';
              // red for hit window
              for(let i=0;i<schedule.length;i++){{
                if(schedule[i].note===p.note && hitEnd[i]>t){{ col='rgb(255,0,0)'; break; }}
              }}
              ctx.fillStyle=col;
              ctx.fill(); ctx.closePath();
              ctx.fillStyle='rgb(248,248,242)'; ctx.textAlign='center'; ctx.textBaseline='middle';
              ctx.font='bold 14px Arial'; ctx.fillText(p.note,p.x,p.y);
            }});
          }}

          function loop() {{
            if(!audio.paused && !audio.ended){{
              updateHits(); draw();
              requestAnimationFrame(loop);
            }}
          }}

          audio.addEventListener('play',()=>{{ processed.fill(false); hitEnd.fill(0); loop(); }});
          audio.addEventListener('pause',()=>{{ draw(); }});
          audio.addEventListener('seeked',()=>{{ processed.fill(false); hitEnd.fill(0); draw(); }});
          audio.addEventListener('ended',()=>{{ draw(); }});

          // initial draw
          window.onload = draw;
        </script>
        """
        components.html(html, height=600)

if __name__=='__main__':
    main()
