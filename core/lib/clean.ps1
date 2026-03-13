# Descobre a pasta do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Sobe duas pastas
$targetDir = Resolve-Path "$scriptDir\..\.."

# Remove __pycache__
Get-ChildItem -Path $targetDir -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove arquivos .pyc
Get-ChildItem -Path $targetDir -Recurse -Filter "*.pyc" | Remove-Item -Force