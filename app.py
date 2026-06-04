from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import pydub
import os
import shutil
import pyloudnorm as pyln
import soundfile as sf
from df.enhance import enhance, init_df, load_audio, save_audio

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cross-platform executable detection
YTDLP = shutil.which("yt-dlp") or "yt-dlp"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

DL_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DL_DIR, exist_ok=True)

model = None
df_state = None

def get_model():
    global model, df_state

    if model is None:
        print("Loading DeepFilterNet model...")
        model, df_state, _ = init_df()
        print("Model ready!")

    return model, df_state

print(f"FFMPEG Path: {FFMPEG}")
print(f"YTDLP Path: {YTDLP}")

print("Current Working Directory:", os.getcwd())
print("Downloads Folder:", DL_DIR)
print("Files:", os.listdir(BASE_DIR))


def apply_speech_eq(input_wav, output_wav):
    """
    Lecture-focused EQ:
    + Slight warmth
    + Speech clarity boost
    - Reduce harsh highs
    """
@app.route('/process', methods=['POST'])
DEF PROCESS():
           
    try:
        subprocess.run([...], check=True)
    except subprocess.CalledProcessError as e:
    return jsonify({"error": str(e) }), 500
   
        
    
@app.route('/')
def index():
    return "Backend Running Successfully"

# =================== YOUTUBE URL ===================
@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    url  = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    video_path  = os.path.join(DL_DIR, 'video.mp4')
    audio_path  = os.path.join(DL_DIR, 'audio.wav')
    clean_audio = os.path.join(DL_DIR, 'clean_audio.wav')
    output_path = os.path.join(DL_DIR, 'output.mp4')

    for f in [video_path, audio_path, clean_audio, output_path]:
        if os.path.exists(f):
            os.remove(f)

    # Step 1: Download video
    subprocess.run([
        YTDLP,
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', video_path,
        url
    ], check=True)

    # Step 2: Extract audio
    subprocess.run([
        FFMPEG, '-y',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        audio_path
    ], check=True)

    # Step 3: DeepFilterNet se clean karo
    print("Cleaning audio...")
    model, df_state = get_model()

    audio_tensor, _ = load_audio(audio_path, sr=df_state.sr())
    enhanced = enhance(model, df_state, audio_tensor)
    save_audio(clean_audio, enhanced, df_state.sr())
    
    # Step 4: Auto normalize
    print("Normalizing volume...")
    data, rate = sf.read(clean_audio)

    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)

    normalized = pyln.normalize.loudness(
        data,
        loudness,
        -16.0
    )

    sf.write(clean_audio, normalized, rate)

    eq_audio = os.path.join(DL_DIR, 'eq_audio.wav')

    print("Applying speech EQ...")
    apply_speech_eq(clean_audio, eq_audio)

    os.remove(clean_audio)
    os.rename(eq_audio, clean_audio)

    print("Done!")

    # Step 5: Merge back
    subprocess.run([
        FFMPEG, '-y',
        '-i', video_path,
        '-i', clean_audio,
        '-c:v', 'copy',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ], check=True)

    return send_file(output_path, as_attachment=True, download_name='clean_video.mp4')


# =================== FILE UPLOAD ===================
@app.route('/process-file', methods=['POST'])
def process_file():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    original_path = os.path.join(
        DL_DIR,
        f"uploaded{os.path.splitext(file.filename)[1]}"
    )
    audio_path    = os.path.join(DL_DIR, 'audio.wav')
    clean_audio   = os.path.join(DL_DIR, 'clean_audio.wav')
    output_path   = os.path.join(DL_DIR, 'output.mp4')

    for f in [original_path, audio_path, clean_audio, output_path]:
        if os.path.exists(f):
            os.remove(f)

    # file save karo
    file.save(original_path)

    # WAV mein convert karo
    audio = pydub.AudioSegment.from_file(original_path)
    audio.export(audio_path, format='wav')

    # Step 3: DeepFilterNet se clean karo
    print("Cleaning uploaded file...")
    model, df_state = get_model()

    audio_tensor, _ = load_audio(audio_path, sr=df_state.sr())
    enhanced = enhance(model, df_state, audio_tensor)
    save_audio(clean_audio, enhanced, df_state.sr())

    # Step 4: Auto normalize
    print("Normalizing volume...")
    data, rate = sf.read(clean_audio)

    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)

    normalized = pyln.normalize.loudness(
        data,
        loudness,
        -16.0
    )

    sf.write(clean_audio, normalized, rate)

    eq_audio = os.path.join(DL_DIR, 'eq_audio.wav')

    print("Applying speech EQ...")
    apply_speech_eq(clean_audio, eq_audio)

    os.remove(clean_audio)
    os.rename(eq_audio, clean_audio)

    print("Done!")

    # video hai to merge karo
    is_video = file.filename.lower().endswith(('.mp4', '.mov', '.avi'))
    if is_video:
        subprocess.run([
            FFMPEG,
            '-y',
            '-i', original_path,
            '-i', clean_audio,
            '-c:v', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_path
        ], check=True)
        return send_file(
            output_path,
            as_attachment=True,
            download_name = 'clean_video.mp4'
        )
        
        

    else:
        return send_file(clean_audio, as_attachment=True,
                        download_name='clean_audio.wav')


@app.route('/health')
def health():
    return jsonify({
        "status": "running"
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


