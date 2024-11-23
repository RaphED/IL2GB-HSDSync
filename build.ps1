#Get in the venv
.\venv\Scripts\Activate.ps1

#get the build version

#initialise the 





pyinstaller --onefile --version-file .\versionfile.txt .\main.py -n ISS


pyinstaller --onefile --version-file .\versionfileUpdater.txt .\ISSupdater.py -n ISSupdater

#create the zip
