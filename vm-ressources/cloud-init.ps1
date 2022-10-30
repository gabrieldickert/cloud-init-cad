#download rhino
Invoke-WebRequest -Uri "https://files.mcneel.com/dujour/exe/20221009/rhino_de-de_7.23.22282.13001.exe" -OutFile "rhino.exe"
#Licening how to automate? => ZOO_Server #rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=STANDALONE LICENSE_KEY=RH70-R6GK-5GT0-3R0A-8R8L-1476 INSTALL_DE=1
./rhino.exe -package -quiet -norestart -passive LICENSE_METHOD=ZOO ZOO_SERVER=10.0.20.6 INSTALL_DE=1 SEND_STATISTICS=0 | Out-Null
#Inital Start of Rhino with EditPythonScript to ensure python works
invoke-expression 'cmd /c start powershell -NoExit -Command { 
$AdminDomain=[System.Net.Dns]::GetHostByName($env:computerName).HostName
$AdminUserName = "cad-master"
$AdminPassword = "!cadmaster1337"
Enable-PSRemoting -Force -SkipNetworkProfileCheck
$credential = New-Object System.Management.Automation.PSCredential @(($AdminDomain + "\" + $AdminUsername), (ConvertTo-SecureString -String $AdminPassword -AsPlainText -Force))
Start-Process -FilePath "C:\Program Files\Rhino 7\System\Rhino.exe"
Start-Process -FilePath "C:\Program Files\Rhino 7\System\Rhino.exe"                                 `                                                    `
}';
Start-Sleep -Seconds 30   
exit 0
