# Download Python
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe" -OutFile "python-3.7.4-amd64.exe"
# Install Python for all users
.\python-3.7.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 | Out-Null
# Load Enviroment Varibales
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = [System.Environment]::ExpandEnvironmentVariables([System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User"))
#download rhino
Invoke-WebRequest -Uri "https://files.mcneel.com/dujour/exe/20220912/rhino_de-de_7.22.22255.05001.exe" -OutFile "rhino.exe"
#Licening how to automate? => ZOO_Server #rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=STANDALONE LICENSE_KEY=RH70-R6GK-5GT0-3R0A-8R8L-1476 INSTALL_DE=1
./rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=ZOO ZOO_SERVER=10.0.20.6 INSTALL_DE=1 SEND_STATISTICS=0 | Out-Null
#Inital Start of Rhino with EditPythonScript to ensure python works
$Process = [Diagnostics.Process]::Start("C:\Program Files\Rhino 7\System\Rhino.exe ", "/nosplash /runscript=""_-EditPythonScript Debugging=On _Enter _Enter""")          
Start-Sleep -Seconds 30   
$id = $Process.Id                        
try {            
    Stop-Process -Id $id -ErrorAction stop            
    #Add Firewall Rule to Match Azure Rule
    netsh advfirewall firewall add rule name="InBoundRule1024" dir=in action=allow protocol=TCP localport=1024
    #Set Port Forwading Rules (Every Request on port 1024 gets forwarded to port 8081)
    netsh interface portproxy add v4tov4 listenport=1024 listenaddress=0.0.0.0 connectport=8081 connectaddress=127.0.0.1
    #Download Server Code
    $serverFileName = "server.py"
    $insideFileName = "inside.py"
    $exeName ="HelloWorld.exe"
    $dll = "RhinoInside.dll"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/server-test.py" -OutFile $serverFileName
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/inside.py" -OutFile $insideFileName
    #Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/HelloWorld.exe" -OutFile $exeName
    #Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gabrieldickert/cloud-init-cad/main/vm-ressources/RhinoInside.dll" -OutFile $dll
    #Install Requirements for Server
    pip install requests
    pip install psutil
    pip install rhinoinside
    #Start Server in new window
    start-process  powershell.exe -ArgumentList "-noExit", "-command", "python server.py"
    #Hopefully Working!
    exit 0 
}
catch {            
    Write-Host "Failed to kill the process"            
}

