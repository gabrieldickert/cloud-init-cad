#Find an exisiting Python PID and kill it to avoid to have multiple Server Instances running
$pythonPId=get-process Py*  |select -expand id

for ($i=0; $i -lt $pythonPID.length; $i++){
    TASKKILL /PID $pythonPID[$i] /F
    Write-Host "Killed Python Process with PID" $pythonPID[$i]
}

$rhinoPID=get-process Rhino*  |select -expand id

for ($i=0; $i -lt $rhinoPID.length; $i++){
    TASKKILL /PID $rhinoPID[$i] /F
    Write-Host "Killed Rhino Process with PID" $rhinoPID[$i]
}
#Start Server Again
start-process  powershell.exe -ArgumentList "-noExit", "-command","python server.py"

exit 0


