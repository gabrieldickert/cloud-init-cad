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
#Download current used Rhino Modul Plugin
$modulPluginName = "rhinogears.rhi"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/rhinogears.rhi" -OutFile $modulPluginName
#Install both Plugins
$currentDir = (Get-Item .).FullName#pwd
#Install for this user
Start-Process -FilePath "C:\Program Files\McNeel\Rhino Installer Engine\x64\rhiexec.exe" -ArgumentList  "$($currentDir)\$($modulPluginName)", "/silent" -Wait
#Try for all users aswell
Start-Process -FilePath "C:\Program Files\McNeel\Rhino Installer Engine\x64\rhiexec.exe" -ArgumentList  "$($currentDir)\$($modulPluginName)", "/admin", "/silent" -Wait
#Add Firewall Rule to Match Azure Rule
netsh advfirewall firewall add rule name="InBoundRule1024" dir=in action=allow protocol=TCP localport=1024
#Set Port Forwading Rules (Every Request on port 1024 gets forwarded to port 8081)
netsh interface portproxy add v4tov4 listenport=1024 listenaddress=0.0.0.0 connectport=8081 connectaddress=127.0.0.1
$rhinoWorker = "RhinoWorker.zip"
Invoke-WebRequest -Uri "https://github.com/gabrieldickert/cloud-init-cad/blob/main/vm-ressources/RhinoWorker.zip?raw=true" -OutFile $rhinoWorker
#Extract RhinoWorker in current dir
Expand-Archive $rhinoWorker -DestinationPath ./
#Download Server Code
$serverFileName = "server.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/server-test.py" -OutFile $serverFileName
#Install Requirements for Server
pip install requests
pip install psutil
#Start Server in new window
start-process  powershell.exe -ArgumentList "-noExit", "-command", "python server.py"
#Hopefully Working!
exit 0 


