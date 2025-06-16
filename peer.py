import threading
import time
import os
import logging
import sys
import socket

from file_manager import FileManager
from peer_server import PeerServer
from peer_client import PeerClient
from strategy import Strategy
from tracker_client import TrackerClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------- CONFIGURAÇÕES INICIAIS --------
# Define o ID do peer com base no argumento passado, ou usa "peer_1" por padrão
PEER_ID = sys.argv[1] if len(sys.argv) > 1 else "peer_1"
TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 8000
BLOCKS_DIR = "peers"
OUTPUT_EXTENSION = ".txt"

# -------- INICIALIZAÇÃO --------
# Cria as instâncias principais do sistema: gerenciamento de blocos, servidor, cliente, estratégia e comunicação com o tracker
file_manager = FileManager(PEER_ID, BLOCKS_DIR)
client = PeerClient(PEER_ID, file_manager)
server = PeerServer(PEER_ID, host="0.0.0.0", port=0, file_manager=file_manager)
strategy = Strategy()
tracker = TrackerClient(TRACKER_HOST, TRACKER_PORT)

# Inicia o servidor em uma thread separada (modo daemon)
server_thread = threading.Thread(target=server.start, daemon=True)
server_thread.start()

# Aguarda o servidor inicializar e obter a porta real
time.sleep(1)
my_port = server.port
my_host = socket.gethostbyname(socket.gethostname())

# Registra este peer no tracker central
if tracker.register(PEER_ID, my_host, my_port):
    logging.info(f"[{PEER_ID}] Registrado no tracker como {my_host}:{my_port}")
else:
    logging.error(f"[{PEER_ID}] Falha ao registrar no tracker")

# Detecta o número total de blocos com base na pasta de blocos principal
main_blocks_dir = os.path.join("peers", "blocks")
if os.path.exists(main_blocks_dir):
    TOTAL_BLOCKS = len([f for f in os.listdir(main_blocks_dir) if f.endswith(".bin")])
    logging.info(f"[{PEER_ID}] Total de blocos detectados: {TOTAL_BLOCKS}")
else:
    TOTAL_BLOCKS = 100  # valor padrão, caso não consiga contar
    logging.warning(f"[{PEER_ID}] Não foi possível detectar blocos. Usando 100 como padrão.")

# -------- Função auxiliar de rarest first --------
# Retorna os blocos ainda não baixados, ordenados do mais raro para o mais comum
def select_rarest_blocks(peer_block_map, my_blocks):
    block_frequency = {}
    for blocks in peer_block_map.values():
        for b in blocks:
            if b not in my_blocks:
                block_frequency[b] = block_frequency.get(b, 0) + 1
    sorted_blocks = sorted(block_frequency.items(), key=lambda x: x[1])
    return [b for b, _ in sorted_blocks]

# -------- LOOP DE TROCA DE BLOCOS --------
# Loop principal de download, roda em background até obter todos os blocos
def download_loop():
    peer_block_map = {}  # mapeia os peers e os blocos que cada um possui
    counter = 0  # usado para controlar a frequência de atualização da estratégia

    while True:
        # Carrega os blocos que este peer já possui
        my_blocks = file_manager.load_blocks()
        logging.info(f"[{PEER_ID}] Blocos atuais: {sorted(my_blocks)}")

        # Se já tiver todos os blocos, tenta reconstruir o arquivo original
        if len(my_blocks) >= TOTAL_BLOCKS:
            logging.info(f"[{PEER_ID}] Todos os blocos foram baixados. Tentando reconstruir...")
            os.makedirs("reconstruidos", exist_ok=True)
            output_path = os.path.join("reconstruidos", f"{PEER_ID}_reconstruido{OUTPUT_EXTENSION}")
            success = file_manager.rebuild_file(output_path, TOTAL_BLOCKS)
            if success:
                logging.info(f"[{PEER_ID}] Arquivo reconstruído com sucesso.")
                logging.info(f"[{PEER_ID}] Permanecendo online como seeder para ajudar outros peers.")
                # Após reconstruir, o peer continua ativo apenas como fonte para outros peers
                while True:
                    time.sleep(60)  # mantém o processo vivo
            else:
                logging.warning(f"[{PEER_ID}] Falha na reconstrução. Esperando mais blocos...")
                time.sleep(3)
                continue

        # Solicita a lista de peers disponíveis ao tracker
        known_peers = tracker.get_peers(PEER_ID)
        peer_block_map.clear()

        # Para cada peer encontrado, obtém a lista de blocos que ele possui
        for peer in known_peers:
            host, port = peer["host"], peer["port"]
            peer_id = f"{host}:{port}"
            blocks = client.get_peer_blocks(host, port)
            if blocks:
                peer_block_map[peer_id] = blocks

        # A cada 5 ciclos (10 segundos), atualiza a estratégia tit-for-tat
        if counter % 5 == 0:
            logging.info(f"[{PEER_ID}] Atualizando estratégia tit-for-tat (a cada 10s) - {time.strftime('%H:%M:%S')}")
            strategy.update_unchoked_peers(
                known_peers=list(peer_block_map.keys()),
                peer_block_map=peer_block_map,
                my_blocks=my_blocks
            )

        # Obtém a lista de peers desbloqueados e blocos mais raros a serem buscados
        unchoked_peers = strategy.get_unchoked_peers()
        rarest_blocks = select_rarest_blocks(peer_block_map, my_blocks)

        # Para cada bloco raro, tenta baixá-lo de um dos peers desbloqueados
        for block_id in rarest_blocks:
            for peer_addr in unchoked_peers:
                host, port = peer_addr.split(":")
                port = int(port)
                if block_id in peer_block_map.get(peer_addr, set()):
                    success = client.request_block(host, port, block_id)
                    if success:
                        break  # Se conseguiu baixar, sai do loop de blocos
            else:
                continue
            break

        time.sleep(2)  # espera entre cada ciclo de tentativa de download
        counter += 1

# Inicia o loop de download em background em uma thread separada
download_thread = threading.Thread(target=download_loop, daemon=True)
download_thread.start()
download_thread.join()
