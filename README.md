# YouTube Lecture to PDF 📹➡️📄

This project is a web application built with Flask that allows users to extract unique frames from a YouTube video and convert them into a downloadable PDF document. Whether you're studying a lecture, reviewing a tutorial, or analyzing a presentation, this app enables you to capture key moments in the form of images and timestamps in a clean PDF format. 

The app is deployed on Render, and it uses the `yt-dlp` library to download YouTube videos and `OpenCV` (CV2) for frame extraction.

## Demo 🎬

You can try the app live here:  
[YouTube Lecture to PDF Demo](https://youtube-lecture-to-pdf.onrender.com/)

## Features ✨

- Download YouTube videos using the powerful `yt-dlp` library.
- Extract unique frames from the video with `OpenCV` (CV2) for precision.
- Generate a PDF that includes the extracted frames and corresponding timestamps.
- Seamlessly download the generated PDF once it's ready.

## Installation ⚙️

### Prerequisites 📦

- Python 3.x
- `pip` (Python package manager)

### Setting Up Locally 🖥️

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/youtube-lecture-to-pdf.git
    cd youtube-lecture-to-pdf
    ```

2. Create a virtual environment and activate it:

   On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask app:
   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000/` to access the app.

## Usage 🖱️

### How to Use the Web App

1. Open the app in your browser: [YouTube Lecture to PDF](https://youtube-lecture-to-pdf.onrender.com/).
2. Paste the URL of the YouTube video you want to convert into the input field.
3. Click the "Generate PDF" button.
4. Wait for the app to process the video. The time it takes will depend on the length of the video.
5. Once processing is completed, download the resulting PDF containing unique frames and their timestamps.

### Input 📥

- The app accepts YouTube video URLs, including:
  - Regular YouTube videos
  - YouTube Shorts
  - Live videos (if available)

### Output 📤

- The app generates a PDF file with:
  - Extracted frames from the video.
  - Timestamps for each frame.
- The output PDF is available for download once processing is complete.

## Contributing 🤝

If you want to contribute to this project, feel free to fork the repository and submit a pull request. Any contributions in terms of bug fixes, improvements, or feature requests are more than welcome!

## License 📝

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

Have any questions or suggestions? Feel free to open an issue or contact the project maintainer. 😄

Enjoy turning your YouTube lectures into neatly organized PDFs! 🎓📄
