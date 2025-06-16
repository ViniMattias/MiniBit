import socket
import threading
import logging
import random
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrackerServer:
    def __init__(self, host="0.0.0.0", port=8000):
        # Inicializa o servidor tracker com IP e porta definidos
        self.host = host
        self.port = port
        self.peers = {}  # Dicionário que armazena os peers registrados: peer_id -> (host, port)
        self.lock = threading.Lock()  # Trava para garantir acesso seguro em múltiplas threads

    def start(self):
        # Inicia o servidor TCP e escuta conexões
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            logging.info(f"[Tracker] Servidor escutando em {self.host}:{self.port}")
            while True:
                client_socket, addr = server.accept()
                client_socket.settimeout(10)
                # Cria uma nova thread para tratar a requisição do peer
                threading.Thread(target=self.handle_peer, args=(client_socket, addr)).start()

    def handle_peer(self, sock, addr):
        # Lida com uma requisição vinda de um peer conectado
        try:
            with sock:
                data = sock.recv(1024).decode().strip()
                if not data:
                    logging.warning(f"[Tracker] Conexão vazia de {addr}")
                    return

                # Comando para registrar peer: REGISTER <peer_id> <host> <port>
                if data.startswith("REGISTER"):
                    parts = data.split()
                    if len(parts) != 4:
                        sock.sendall(b"ERROR Invalid REGISTER format")
                        return
                    _, peer_id, host, port = parts
                    with self.lock:
                        self.peers[peer_id] = (host, int(port))  # Salva o peer no dicionário
                    logging.info(f"[Tracker] Registrado {peer_id} em {host}:{port}")
                    sock.sendall(b"OK")  # Resposta de sucesso

                # Comando para obter lista de peers: GET_PEERS <peer_id>
                elif data.startswith("GET_PEERS"):
                    parts = data.split()
                    if len(parts) != 2:
                        sock.sendall(b"ERROR Invalid GET_PEERS format")
                        return
                    _, peer_id = parts
                    with self.lock:
                        # Filtra os peers removendo o próprio solicitante
                        other_peers = [
                            {"peer_id": pid, "host": host, "port": port}
                            for pid, (host, port) in self.peers.items()
                            if pid != peer_id
                        ]
                        # Retorna até 5 peers aleatórios
                        sample = random.sample(other_peers, min(5, len(other_peers)))
                    sock.sendall(json.dumps(sample).encode())  # Envia a lista em formato JSON

                else:
                    # Comando não reconhecido
                    logging.warning(f"[Tracker] Comando inválido de {addr}: {data}")
                    sock.sendall(b"ERROR Invalid command")
        except Exception as e:
            # Caso ocorra algum erro no tratamento da requisição
            logging.warning(f"[Tracker] Erro com cliente {addr}: {e}")

if __name__ == "__main__":
    # Inicia o servidor quando o script é executado diretamente
    tracker = TrackerServer()
    tracker.start()
