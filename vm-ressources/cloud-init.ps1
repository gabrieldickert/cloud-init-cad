# Download Python
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe" -OutFile "python-3.7.4-amd64.exe"
# Install Python for all users
.\python-3.7.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 | Out-Null
# Load Enviroment Varibales
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = [System.Environment]::ExpandEnvironmentVariables([System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User"))
#download rhino
Invoke-WebRequest -Uri "https://files.mcneel.com/dujour/exe/20221009/rhino_de-de_7.23.22282.13001.exe" -OutFile "rhino.exe"
#Licening how to automate? => ZOO_Server #rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=STANDALONE LICENSE_KEY=RH70-R6GK-5GT0-3R0A-8R8L-1476 INSTALL_DE=1
./rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=ZOO ZOO_SERVER=10.0.20.6 INSTALL_DE=1 SEND_STATISTICS=0 | Out-Null
#Download Server Code
$serverFileName = "server.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/teststart.py" -OutFile $serverFileName
start-process  powershell.exe -ArgumentList "-noExit", "-command", "python server.py"
exit 0
