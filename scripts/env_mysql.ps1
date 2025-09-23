# Use: .\scripts\env_mysql.ps1
$env:MYSQL_NAME = "kifome"
$env:MYSQL_USER = "kifome_user"
$env:MYSQL_PASSWORD = "SUA_SENHA_AQUI"
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
Write-Host "Variáveis definidas: MYSQL_*"
