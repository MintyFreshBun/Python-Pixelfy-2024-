# Python Pixelfy

Turn a photo into pixel art in your browser. Upload an image, adjust the color and dithering controls, and save the result.

[![Flask](https://img.shields.io/badge/Flask-3.1-blue)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

## Features

- Pixel-art conversion with adjustable brightness, contrast, dithering, and color count
- Grayscale output or a selection of built-in color palettes
- Original/result preview toggle and JPEG download

## Requirements

- Python 3.10 or newer
- pip

The app uses Flask, Pillow, BlendModes, and Werkzeug. Exact tested versions are listed in [`requirements.txt`](requirements.txt).

## Run locally

1. Clone the repository and enter its folder:

   ```bash
   git clone https://github.com/MintyFreshBun/Python-Pixelfy-2024-.git
   cd Python-Pixelfy-2024-
   ```

2. Create and activate a virtual environment:

   **Windows (PowerShell):**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the project dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the development server from the repository folder:

   ```bash
   python new_main.py
   ```

5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and upload an image.

The app loads its palette and pattern files from the repository, so run it from the project folder. Bulma is loaded from a CDN, so an internet connection is needed for the page styling.

## Run tests

With the virtual environment active, run:

```bash
python -m unittest discover -s tests
```

## Notes

`new_main.py` starts Flask's development server. Do not expose it directly to the internet or use it as a production server.

## Author

**Miguel Amaral** — developer
