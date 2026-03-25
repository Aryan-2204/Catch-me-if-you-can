AI Pokémon Chase

Local run

1. Create a virtual environment (macOS/Linux):
   python3 -m venv .venv
   source .venv/bin/activate
2. Install dependencies:
   pip install -r requirements.txt
3. Run:
   python3 main.py

Building a macOS app (optional)

1. Activate venv and install requirements including pyinstaller.
2. pyinstaller --onefile --windowed main.py

Notes
- This project uses Pygame CE. If assets/fonts are missing the game falls back to system fonts/placeholders.
- Clean corrupted backups (`main_fixed.py`, `main_fixed_original.py`) to avoid syntax errors during lint/compile.
