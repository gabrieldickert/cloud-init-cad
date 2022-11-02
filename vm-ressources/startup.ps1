start-process  powershell.exe -ArgumentList "-noExit", "-command", "& 'C:\Program Files\Rhino 7\System\Rhino.exe'"
$RegistryPath = ‘HKLM:\SOFTWARE\Microsoft\Windows Azure\ScriptHandler’
Set-ItemProperty $RegistryPath ‘MreSeqNumFinished’ -Value “1” -Type String
exit 0