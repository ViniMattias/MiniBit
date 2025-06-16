# Remove a pasta completa de peers (inclui peer_1 a peer_n + blocks)
Remove-Item -Path peers -Recurse -Force -ErrorAction SilentlyContinue

# Remove reconstruídos
Remove-Item -Path reconstruidos -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Limpeza concluida. Pronto para nova execucao."