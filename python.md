# Python virtual environment

#### If you are running Python 3.4+, you can use the venv module:
```
python -m venv _python
```

#### This command creates a venv in the specified directory and copies pip into it as well.

#### Activate:
For Windows Powershell:
```
.\_python\Scripts\Activate.ps1
```

#### Deactivate:
```
deactivate
```

#### Install a compatible version:
```
pyenv install 3.12.x
```

#### List all available versions
```
pyenv install -l
```

#### Set it for the project:
```
pyenv install 3.12.x
```
#### Create requirements.txt:
```
pip3 freeze > requirements.txt
```

#### Install packages:
```
pip3 install -r requirements.txt
```

#### Package your Python script
Add `pyinstaller` to your requirements file.

```
pip install pyinstaller
```
#### Build the app
```
pyinstaller --onefile --windowed --icon=your_icon.ico --add-data "games.db;." display_app.py
```
After running the command, PyInstaller will generate a dist folder containing the standalone executable file for your script.

