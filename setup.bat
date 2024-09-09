@echo off
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip install transformers
echo Virtual environment setup complete.
pause
