function Test-CondaInstallation {
    # This function dosen't work in a lot of cases (since conda is genrally limited to powerhsell)
    $executablePath = Get-Command -Name conda -ErrorAction SilentlyContinue
    
    return $executablePath -ne $null
    
}
# Check if Conda is already installed
$condaInstalled = Test-CondaInstallation

if (-not $condaInstalled) {
    # Download the Anaconda installer (you can change the URL if needed)
    $condaInstallerUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $installerPath = Join-Path $env:TEMP "Anaconda3Installer.exe"

    Write-Host "Conda is not installed. Downloading and installing Anaconda..."
    
    # Download the Anaconda installer
    Invoke-WebRequest -Uri $condaInstallerUrl -OutFile $installerPath

    # Install Anaconda silently
    Write-Host "Conda installer downloaded. Installing Anaconda..."
    Start-Process -Wait -FilePath $installerPath -ArgumentList "/S", "/D=$env:USERPROFILE\miniconda3" -PassThru

    # Clean up the installer
    Remove-Item $installerPath

    Write-Host "Anaconda has been installed."
    
    # Add Conda to the system PATH
    $condaPath = Join-Path $env:USERPROFILE "miniconda3"
    $env:Path += ";$condaPath;$condaPath\Scripts;$condaPath\Library\bin"
    Write-Host "Running conda ."
    conda init powershell
}
else {
    Write-Host "Conda is already installed."
}


# Verify Conda installation
conda --version
conda update -y --all

Write-Host "Installing mamba."
conda install -y -c conda-forge mamba
Write-Host "Creating a new env."
mamba env create -y -f ..\environment_windows.yml
Write-Host "Conda is installed. Open the anaconda prompt and run 'conda activate rillgen2d'."