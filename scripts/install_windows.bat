@echo off
echo Installing Miniconda...
:: Specify the installation path for Miniconda
set INSTALL_PATH=%USERPROFILE%\Miniconda3
:: Download and install Miniconda
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
start /wait Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=0 /D=%INSTALL_PATH%
:: Remove the installer
del Miniconda3-latest-Windows-x86_64.exe
:: Initialize Conda
call %INSTALL_PATH%\Scripts\activate.bat
:: Install mamba
call conda install mamba -c conda-forge -y
:: Create a new Conda environment
call mamba env create -f ..\environment_windows.yml -y
:: Activate the new environment
call conda activate rillgen2d
:: Your installation script is complete. 
echo Installation complete. 
set "batchDir=%~dp0"
set "twoFoldersAbove=%batchDir%..\"

echo The filepath to rillgen2d is: %twoFoldersAbove%
echo Launch the Anaconda Prompt then enter 'conda activate rillgen2d', then enter 'cd %twoFoldersAbove%'
pause

