Fake Virus Prank - Package
Files:
- prank_with_sounds_and_browser.py   (main script)
- assets/sounds/*.wav                (sound effects included)
- assets/icon.ico                    (optional icon)
- requirements.txt

How to run (source):
1) Create venv: python -m venv venv
2) Activate venv and install PyQt5 or PyQt6:
   pip install PyQt6    OR    pip install PyQt5
3) Run: python prank_with_sounds_and_browser.py

How to build single exe with PyInstaller:
Windows example:
pyinstaller --onefile --windowed --clean --add-data "assets;assets" --icon "assets/icon.ico" prank_with_sounds_and_browser.py

Linux/macOS example (use colon separator):
pyinstaller --onefile --windowed --clean --add-data "assets:assets" --icon "assets/icon.ico" prank_with_sounds_and_browser.py

Safety:
- This prank is intentionally non-destructive and shows clear PRANK labels.
- Do NOT run on systems without explicit permission.