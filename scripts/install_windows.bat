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
call conda install mamba -c conda-forge
:: Create a new Conda environment
call mamba env create -f ..\environment_windows.yml -y
:: Activate the new environment
call conda activate rillgen2d
:: Your installation script is complete. 
echo Installation complete. 
echo Launch the Anaconda Prompt then enter 'conda activate rillgen2d', then %cd%
pause

