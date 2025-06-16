import socket
import logging
from typing import Set, Optional

# Fallback para protocolo simples (até termos o real)
# Monta uma mensagem GET para solicitar um bloco específico
def build_get(block_id: int) -> str:
    return f"GET {block_id}"

# Monta uma mensagem LIST para solicitar a lista de blocos disponíveis de um peer
def build_list() -> str:
    return "LIST"

# Interpreta a mensagem recebida de outro peer e extrai o comando e o conteúdo
def parse_message(data: bytes):
    try:
        if data.startswith(b"BLOCKS "):
            payload = data[7:]
            return "BLOCKS", None, payload

        elif data.startswith(b"BLOCK "):
            parts = data.split(b" ", 2)
            if len(parts) == 3:
                block_id = int(parts[1])
                payload = parts[2]
                return "BLOCK", block_id, payload

    except:
        pass  # Em caso de erro de parsing, retorna None
    return None, None, None


class PeerClient:
    def __init__(self, peer_id: str, file_manager):
        # Inicializa o cliente do peer, com o ID do peer e o gerenciador de arquivos
        self.peer_id = peer_id
        self.file_manager = file_manager

    def get_peer_blocks(self, host: str, port: int) -> Optional[Set[int]]:
        # Conecta-se a outro peer e solicita a lista de blocos disponíveis
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(build_list().encode())
                data = sock.recv(4096)
                cmd, _, payload = parse_message(data)

                if cmd == "BLOCKS" and payload:
                    decoded = payload.decode()
                    block_ids = list(map(int, decoded.split(","))) if decoded else []
                    return set(block_ids)  # Retorna o conjunto de blocos do peer

        except Exception as e:
            logging.warning(f"[{self.peer_id}] Falha ao obter blocos de {host}:{port} - {e}")
        return None  # Se falhar, retorna None

    def request_block(self, host: str, port: int, block_id: int) -> bool:
        # Solicita um bloco específico a outro peer e salva o bloco, se recebido com sucesso
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(build_get(block_id).encode())
                response = sock.recv(4096 + 64)

                cmd, received_id, data = parse_message(response)
                if cmd == "BLOCK" and received_id == block_id and data:
                    self.file_manager.save_block(block_id, data)
                    logging.info(f"[{self.peer_id}] Bloco {block_id} recebido de {host}:{port}")
                    return True  # Sucesso na requisição

        except Exception as e:
            logging.warning(f"[{self.peer_id}] Erro ao solicitar bloco {block_id} de {host}:{port} - {e}")
        return False  # Falha na requisição
