import socket
import json

class TrackerClient:
    def __init__(self, host, port):
        # Armazena o host e a porta do servidor tracker
        self.host = host
        self.port = port

    def register(self, peer_id, ip, port):
        # Envia uma mensagem de registro para o tracker no formato:
        # REGISTER <peer_id> <ip> <port>
        try:
            with socket.create_connection((self.host, self.port), timeout=5) as s:
                msg = f"REGISTER {peer_id} {ip} {port}"
                s.sendall(msg.encode())  # Envia a mensagem ao tracker
                response = s.recv(1024).decode()  # Aguarda resposta
                return response.strip() == "OK"  # Retorna True se registro for bem-sucedido
        except:
            return False  # Retorna False se ocorrer erro na conexão

    def get_peers(self, peer_id):
        # Solicita ao tracker a lista de peers disponíveis, exceto ele mesmo
        # Envia: GET_PEERS <peer_id>
        try:
            with socket.create_connection((self.host, self.port), timeout=5) as s:
                msg = f"GET_PEERS {peer_id}"
                s.sendall(msg.encode())  # Envia a solicitação
                response = s.recv(4096).decode()  # Recebe resposta em JSON
                return json.loads(response)  # Converte JSON para lista de peers (dicionários)
        except:
            return []  # Retorna lista vazia em caso de erro
