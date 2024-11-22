.\venv\Scripts\Activate.ps1



pyinstaller --onefile --version-file .\versionfile.txt .\main.py -n ISSS


pyinstaller --onefile --version-file .\versionfileUpdater.txt .\updaterISSS.py -n updaterIsss
