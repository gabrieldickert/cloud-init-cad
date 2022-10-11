echo Download Python...

curl -o python-3.7.4-amd64.exe https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe

echo Install Python for all users..

.\python-3.7.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Python is now installed...

echo Downloading Rhino...

curl -o rhino.exe https://files.mcneel.com/dujour/exe/20220912/rhino_de-de_7.22.22255.05001.exe

echo Installing Rhino...
rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=ZOO ZOO_SERVER=10.0.0.1 INSTALL_DE=1

echo Download Rhino Plugin for REST API Server...

echo Installing Rhino Plugin...

echo Set Port Forwading Rules...

echo Installing Python Moduls
pip install requests

echo Starting Python Server...
python 
