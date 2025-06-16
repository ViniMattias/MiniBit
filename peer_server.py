import socket
import threading
import logging
from file_manager import FileManager
from protocol import parse_message, build_block, build_blocks_list, build_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PeerServer:
    def __init__(self, peer_id, host='0.0.0.0', port=0, file_manager: FileManager = None):
        # Inicializa o servidor com o ID do peer, o IP/porta para escutar, e o gerenciador de arquivos
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.file_manager = file_manager
        self.running = True  # Controla se o servidor deve continuar rodando

    def start(self):
        """
        Inicia o servidor TCP e escuta conexões de outros peers.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reuso da porta
        server.bind((self.host, self.port))  # Associa o socket ao endereço e porta
        server.listen()
        self.port = server.getsockname()[1]  # Captura a porta real usada (caso tenha sido 0)
        logging.info(f"[{self.peer_id}] Servidor ouvindo em {self.host}:{self.port}")

        # Loop principal: aceita conexões e trata cada uma em uma thread separada
        while self.running:
            try:
                client_socket, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            except Exception as e:
                logging.error(f"[{self.peer_id}] Erro ao aceitar conexão: {e}")

    def handle_client(self, sock, addr):
        """
        Trata a solicitação de um peer (LIST ou GET).
        """
        try:
            with sock:
                data = sock.recv(4096)  # Recebe a mensagem enviada pelo peer cliente
                cmd, block_id, payload = parse_message(data)  # Interpreta a mensagem

                if cmd == "GET":
                    # Se for um pedido de bloco, tenta obter o bloco e enviar
                    block_data = self.file_manager.get_block(block_id)
                    if block_data:
                        sock.sendall(build_block(block_id, block_data))
                    else:
                        sock.sendall(build_error("Block not found").encode())

                elif cmd == "LIST":
                    # Se for um pedido de lista de blocos, envia todos os blocos disponíveis
                    blocks = self.file_manager.load_blocks()
                    response = build_blocks_list(blocks)
                    sock.sendall(response.encode())

                else:
                    # Qualquer comando inválido é respondido com mensagem de erro
                    sock.sendall(build_error("Invalid command").encode())

        except Exception as e:
            logging.error(f"[{self.peer_id}] Erro com cliente {addr}: {e}")
