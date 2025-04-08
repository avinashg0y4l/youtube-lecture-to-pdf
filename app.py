from flask import Flask, request, render_template, send_file
import tempfile
import os
import re
from fpdf import FPDF
from PIL import Image
import yt_dlp
import cv2
from skimage.metrics import structural_similarity as compare_ssim
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# ---------- Helper Functions ----------

def download_video(url, output_file, cookie_path=None):
    if os.path.exists(output_file):
        os.remove(output_file)

    ydl_opts = {
        'outtmpl': output_file,
        'format': 'best',
        'quiet': True
    }

    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def get_video_id(url):
    patterns = [
        r"shorts\/(\w+)",
        r"youtu\.be\/([\w\-_]+)(\?.*)?",
        r"v=([\w\-_]+)",
        r"live\/(\w+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_unique_frames(video_file, output_folder, n=3, ssim_threshold=0.8):
    cap = cv2.VideoCapture(video_file)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    last_frame = None
    frame_number = 0
    last_saved_frame_number = -1
    timestamps = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % n == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.resize(gray_frame, (128, 72))

            if last_frame is not None:
                similarity = compare_ssim(gray_frame, last_frame, data_range=gray_frame.max() - gray_frame.min())
                if similarity < ssim_threshold and (frame_number - last_saved_frame_number > fps):
                    frame_path = os.path.join(output_folder, f'frame{frame_number:04d}_{frame_number // fps}.png')
                    cv2.imwrite(frame_path, frame)
                    timestamps.append((frame_number, frame_number // fps))
                    last_saved_frame_number = frame_number
            else:
                frame_path = os.path.join(output_folder, f'frame{frame_number:04d}_{frame_number // fps}.png')
                cv2.imwrite(frame_path, frame)
                timestamps.append((frame_number, frame_number // fps))
                last_saved_frame_number = frame_number

            last_frame = gray_frame

        frame_number += 1

    cap.release()
    return timestamps

def convert_frames_to_pdf(input_folder, output_buffer, timestamps):
    frame_files = sorted(os.listdir(input_folder), key=lambda x: int(x.split('_')[0].replace('frame', '')))
    pdf = FPDF("L")
    pdf.set_auto_page_break(0)

    for frame_file, (frame_number, timestamp_seconds) in zip(frame_files, timestamps):
        frame_path = os.path.join(input_folder, frame_file)
        image = Image.open(frame_path)
        pdf.add_page()
        pdf.image(frame_path, x=0, y=0, w=pdf.w, h=pdf.h)

        # Format timestamp
        timestamp = f"{timestamp_seconds // 3600:02d}:{(timestamp_seconds % 3600) // 60:02d}:{timestamp_seconds % 60:02d}"

        # Determine text color based on brightness
        x, y, width, height = 5, 5, 60, 15
        region = image.crop((x, y, x + width, y + height)).convert("L")
        mean_pixel_value = region.resize((1, 1)).getpixel((0, 0))

        if mean_pixel_value < 64:
            pdf.set_text_color(255, 255, 255)
        else:
            pdf.set_text_color(0, 0, 0)

        pdf.set_xy(x, y)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 0, timestamp)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    output_buffer.write(pdf_bytes)
    output_buffer.seek(0)

def get_video_title(url, cookie_path=None):
    ydl_opts = {
        'skip_download': True,
        'ignoreerrors': True,
        'quiet': True,
    }
    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            return "video"
        title = info.get('title', 'video').strip()
        for char in r'\/:*?"<>|':
            title = title.replace(char, '-')
        return title.strip('.')

# ---------- Routes ----------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        cookie_file = request.files.get('cookie_file')

        if not url:
            return render_template('index.html', message="Please provide a YouTube URL.")

        # Save cookies if uploaded
        cookie_path = None
        if cookie_file and cookie_file.filename.endswith('.txt'):
            filename = secure_filename(cookie_file.filename)
            cookie_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cookie_file.save(cookie_path)

        try:
            video_id = get_video_id(url)
            if not video_id:
                return render_template('index.html', message="Invalid YouTube URL.")

            video_title = get_video_title(url, cookie_path)
            sanitized_title = video_title.replace(" ", "_")
            video_file = os.path.join(tempfile.gettempdir(), f"{sanitized_title}.mp4")

            # Download the YouTube video
            download_video(url, video_file, cookie_path)

            # Frame extraction and PDF generation
            with tempfile.TemporaryDirectory() as tmp_dir:
                frame_folder = os.path.join(tmp_dir, "frames")
                os.makedirs(frame_folder)

                timestamps = extract_unique_frames(video_file, frame_folder)

                pdf_buffer = BytesIO()
                convert_frames_to_pdf(frame_folder, pdf_buffer, timestamps)

            os.remove(video_file)
            if cookie_path and os.path.exists(cookie_path):
                os.remove(cookie_path)

            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{sanitized_title}.pdf"
            )

        except Exception as e:
            return render_template('index.html', message=f"An error occurred: {str(e)}")

    return render_template('index.html')

# ---------- Run the App ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
