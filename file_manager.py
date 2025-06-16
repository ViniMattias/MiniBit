import os
import random
from typing import Set, Optional

BLOCK_SIZE = 1024  # Tamanho do bloco em bytes
NUM_PEERS = 5


class FileManager:
    def __init__(self, peer_id: str, base_dir: str = "peers"):
        # Inicializa o gerenciador de arquivos do peer, definindo o diretório onde os blocos serão armazenados
        self.peer_id = peer_id
        self.blocks_dir = os.path.join(base_dir, peer_id, "blocks")
        os.makedirs(self.blocks_dir, exist_ok=True)
        self.blocks = {}  # Cache para armazenar blocos já carregados em memória

    def load_blocks(self) -> Set[int]:
        # Carrega todos os blocos disponíveis no diretório do peer e retorna um conjunto com os índices dos blocos
        blocks = set()
        for filename in os.listdir(self.blocks_dir):
            if filename.startswith("block_") and filename.endswith(".bin"):
                try:
                    index = int(filename.split("_")[1].split(".")[0])
                    blocks.add(index)
                except:
                    continue  # Ignora arquivos que não seguem o padrão esperado
        return blocks

    def save_block(self, block_num: int, data: bytes) -> None:
        # Salva um bloco no disco e também armazena em cache
        path = os.path.join(self.blocks_dir, f"block_{block_num}.bin")
        with open(path, "wb") as f:
            f.write(data)
        self.blocks[block_num] = data

    def get_block(self, block_num: int) -> Optional[bytes]:
        # Retorna o conteúdo de um bloco, buscando primeiro no cache e depois no disco, se necessário
        if block_num in self.blocks:
            return self.blocks[block_num]

        path = os.path.join(self.blocks_dir, f"block_{block_num}.bin")
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
                self.blocks[block_num] = data
                return data
        return None  # Se o bloco não for encontrado, retorna None

    def rebuild_file(self, output_path: str, total_blocks: int) -> bool:
        # Reconstrói o arquivo original unindo os blocos em ordem e salvando no caminho especificado
        missing = []
        with open(output_path, "wb") as output:
            for i in range(total_blocks):
                data = self.get_block(i)
                if data:
                    output.write(data)
                else:
                    missing.append(i)
        if missing:
            print(f"[{self.peer_id}] Faltam blocos para reconstrução: {missing}")
            return False  # Arquivo incompleto
        return True  # Arquivo reconstruído com sucesso


def split_and_distribute(filepath: str, output_dir: str = "peers", block_size: int = BLOCK_SIZE, num_peers: int = NUM_PEERS):
    blocks_path = os.path.join(output_dir, "blocks")
    os.makedirs(blocks_path, exist_ok=True)

    # Cria pastas dos peers
    peer_dirs = []
    for i in range(1, num_peers + 1):
        peer_dir = os.path.join(output_dir, f"peer_{i}", "blocks")
        os.makedirs(peer_dir, exist_ok=True)
        peer_dirs.append(peer_dir)

    # Divide o arquivo em blocos e salva cada um como um arquivo separado
    block_paths = []
    with open(filepath, "rb") as f:
        index = 0
        while chunk := f.read(block_size):
            path = os.path.join(blocks_path, f"block_{index}.bin")
            with open(path, "wb") as bf:
                bf.write(chunk)
            block_paths.append(path)
            index += 1

    total_blocks = len(block_paths)
    print(f"[SETUP] Total de blocos criados: {total_blocks}")

    # Garante que cada bloco vá para pelo menos um peer
    for b in range(total_blocks):
        selected_peer = random.choice(peer_dirs)
        src = block_paths[b]
        dst = os.path.join(selected_peer, f"block_{b}.bin")
        with open(src, "rb") as s, open(dst, "wb") as d:
            d.write(s.read())

    # Adiciona blocos extras aleatórios para simular distribuição real entre os peers
    for peer_dir in peer_dirs:
        extra_blocks = random.sample(range(total_blocks), random.randint(1, total_blocks - 1))
        for b in extra_blocks:
            src = block_paths[b]
            dst = os.path.join(peer_dir, f"block_{b}.bin")
            if not os.path.exists(dst):
                with open(src, "rb") as s, open(dst, "wb") as d:
                    d.write(s.read())

    # Mostrar blocos por peer
    for i, peer_dir in enumerate(peer_dirs, start=1):
        count = len([f for f in os.listdir(peer_dir) if f.endswith(".bin")])
        print(f"[SETUP] Peer {i} recebeu {count} blocos.")

    return total_blocks
