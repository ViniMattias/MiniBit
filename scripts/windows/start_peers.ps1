# Detecta número de peers baseado nas pastas peers/peer_*
$PeerDirs = Get-ChildItem -Path "peers" -Directory -Filter "peer_*"
$NumPeers = $PeerDirs.Count

# Conta quantos blocos foram gerados (em peers/blocks)
$TotalBlocks = (Get-ChildItem -Path "peers\blocks" -Filter "*.bin").Count

$BasePort = 6000

Write-Host "Iniciando $NumPeers peers com $TotalBlocks blocos..."

for ($i = 1; $i -le $NumPeers; $i++) {
    $PeerId = "peer_$i"
    $Port = $BasePort + $i

    Write-Host "Iniciando $PeerId na porta $Port"

    # Abre nova janela PowerShell que não fecha
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "python peer.py $PeerId $Port $TotalBlocks"

    Start-Sleep -Milliseconds 500
}