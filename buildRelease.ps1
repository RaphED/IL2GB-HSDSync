

#Build global parameters
$BuildDir = "build"
$DistDir = "release"
$zipFile = "ISS.zip"

#clear build folder
Remove-Item -Path $BuildDir -Recurse -Force
New-Item -Path $BuildDir -ItemType Directory

#clear release folder
Remove-Item -Path $DistDir -Recurse -Force
New-Item -Path $DistDir -ItemType Directory

#Activate the venv
.\venv\Scripts\Activate.ps1

#VERSIONNING
$VERSION = python versionManager.py

#Script to generate version files from the template
function New-VersionFile {
    param(
        [string]$version,
        [string]$exeFileName,
        [string]$targetVersionFileName
    )

    $fileContent = Get-Content versionFileTemplate.txt -Raw
    $fileContent = $fileContent -replace '\$VERSION', $version
    $fileContent = $fileContent -replace '\$FILENAME', $exeFileName
    Set-Content -Path "$BuildDir\$targetVersionFileName" -Value $fileContent
}

function New-exeFile {
    param(
        [string]$appName,
        [string]$pythonMainFile
    )

    #generate the version file for that exe
    New-VersionFile -version $VERSION -exeFileName "$appName.exe" -targetVersionFileName $appName"_versionFile"
    
    
    pyinstaller --onefile --clean ".\$pythonMainFile" `
        --name $appName `
        --distpath $DistDir `
        --specpath $BuildDir `
        --version-file $appName"_versionFile" `
        --icon "Ressources\iss.ico" `
        --add-data="Ressources/*:Ressources" `
        --add-data="Ressources/forest-light/*:Ressources/forest-light"
}

function New-exeFileFromSpecFile {
    param(
        [string]$appName
    )

    #generate the version file for that exe
    New-VersionFile -version $VERSION -exeFileName "$appName.exe" -targetVersionFileName $appName"_versionFile"

    pyinstaller --clean "$appName.spec" --distpath $DistDir
}

#Copy ressources to the build folder
#Copy-Item -Path ".\Ressources"  -Destination ".\$BuildDir\Ressources" -Recurse

#Creation of the main EXE
#New-exeFile -appName "ISS" -pythonMain "main.py"
New-exeFileFromSpecFile -appName "ISS"

#add a Subscription folder with an example in it
New-Item -Path "$DistDir\Subscriptions" -ItemType Directory
Copy-Item -Path "SubscriptionExamples\IRRE Full.iss" -Destination "$DistDir\Subscriptions\IRRE Full.iss" -Recurse

#create the zip with all files in the dist
Compress-Archive -Path "$DistDir\*" -DestinationPath $DistDir"\"$zipFile

#Create the updater exe
New-exeFile -appName "ISSUpdater" -pythonMain "ISSupdater.py"

