Add-Type -AssemblyName System.Windows.Forms

$dlg = New-Object System.Windows.Forms.OpenFileDialog
$dlg.Filter = "Imagens|*.jpg;*.jpeg;*.tif;*.tiff;*.png"

if ($dlg.ShowDialog() -ne "OK") { exit }

$path = $dlg.FileName

$shell = New-Object -ComObject Shell.Application
$folder = $shell.Namespace((Split-Path $path))
$file = $folder.ParseName((Split-Path $path -Leaf))

"Arquivo: $path"
"-----------------------------"

# percorre TODOS os campos conhecidos pelo Windows
for ($i = 0; $i -lt 350; $i++) {
    $nome = $folder.GetDetailsOf($null, $i)
    if ($nome) {
        $valor = $folder.GetDetailsOf($file, $i)
        if ($valor) {
            "{0}: {1}" -f $nome, $valor
        }
    }
}
# opcional: salvar em TXT
$salvar = Read-Host "Deseja salvar os metadados em TXT? (s/n)"
if ($salvar -eq "s") {
    $saida = [System.IO.Path]::ChangeExtension($foto, ".metadados.txt")
    & $exiftool -a -u -g1 "$foto" > "$saida"
    Write-Host "Arquivo salvo em:"
    Write-Host $saida
}
