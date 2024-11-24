

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
function generate-versionFile{
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

function generate-exeFile{
    param(
        [string]$appName,
        [string]$pythonMainFile
    )

    generate-versionFile -version $VERSION -exeFileName "$appName.exe" -targetVersionFileName $appName"_versionFile"
    pyinstaller --onefile  ".\$pythonMainFile" --name $appName --distpath $DistDir --clean --specpath $BuildDir --version-file $appName"_versionFile"
}

#Creation of the two program exe
generate-exeFile -appName "ISS" -pythonMain "main.py"
generate-exeFile -appName "ISSUpdater" -pythonMain "ISSupdater.py"

#add a Subscription folder with an example in it
New-Item -Path "$DistDir\Subscriptions" -ItemType Directory
Copy-Item -Path "SubscriptionExamples\Example.iss" -Destination "$DistDir\Subscriptions\Example.iss" -Recurse


#create the zip with all files in the dist
Compress-Archive -Path "$DistDir\*" -DestinationPath $DistDir"\"$zipFile

