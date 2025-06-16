#!/bin/bash

echo "Iniciando peers..."

num_peers=$(find peers -maxdepth 1 -type d -name 'peer_*' | wc -l)


os_name="$(uname)"

for i in $(seq 1 $num_peers)
do
  if [[ "$os_name" == "Linux" ]]; then
    gnome-terminal -- bash -c "python3 peer.py peer_$i; exec bash"
  elif [[ "$os_name" == "Darwin" ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd $(pwd); python3 peer.py peer_$i\""
  else
    echo "Sistema operacional não suportado."
    exit 1
  fi
done
