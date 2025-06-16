from typing import Optional, Tuple, Iterable
import logging

# Constantes dos comandos suportados
CMD_GET = "GET"         # Solicita um bloco específico
CMD_LIST = "LIST"       # Solicita a lista de blocos disponíveis
CMD_BLOCK = "BLOCK"     # Resposta com o bloco solicitado
CMD_BLOCKS = "BLOCKS"   # Resposta com a lista de blocos disponíveis
CMD_ERROR = "ERROR"     # Mensagem de erro
CMD_INVALID = "INVALID" # Mensagem mal formatada
CMD_UNKNOWN = "UNKNOWN" # Comando desconhecido

# ----------------------
# Funções de montagem
# ----------------------

def build_get(block_id: int) -> str:
    # Monta a mensagem GET <id> para pedir um bloco
    return f"{CMD_GET} {block_id}"

def build_list() -> str:
    # Monta a mensagem LIST para pedir a lista de blocos
    return CMD_LIST

def build_block(block_id: int, data: bytes) -> bytes:
    # Monta a mensagem BLOCK <id> <conteúdo> para enviar um bloco
    return f"{CMD_BLOCK} {block_id} ".encode() + data

def build_blocks_list(block_ids: Iterable[int]) -> str:
    # Monta a mensagem BLOCKS com os IDs dos blocos disponíveis
    return f"{CMD_BLOCKS} {','.join(map(str, sorted(block_ids)))}"

def build_error(msg: str) -> str:
    # Monta uma mensagem de erro com a descrição fornecida
    return f"{CMD_ERROR} {msg}"

# ----------------------
# Função de parsing
# ----------------------

def parse_message(message: bytes) -> Tuple[str, Optional[int], Optional[bytes]]:
    """
    Interpreta uma mensagem recebida.

    Retorna uma tupla:
    - tipo do comando (str)
    - ID do bloco (se aplicável)
    - dados binários (se aplicável)
    """
    try:
        # Trata mensagens do tipo BLOCK com dados binários
        if message.startswith(f"{CMD_BLOCK} ".encode()):
            parts = message.split(b' ', 2)
            if len(parts) < 3:
                return CMD_BLOCK, int(parts[1]), b''
            return CMD_BLOCK, int(parts[1]), parts[2]

        # Decodifica a mensagem como string para tratar os outros tipos
        decoded = message.decode().strip()

        if decoded.startswith(CMD_GET):
            # Mensagem GET <id>
            parts = decoded.split()
            if len(parts) == 2 and parts[1].isdigit():
                return CMD_GET, int(parts[1]), None
            return CMD_INVALID, None, None

        if decoded == CMD_LIST:
            # Mensagem LIST
            return CMD_LIST, None, None

        if decoded.startswith(CMD_BLOCKS):
            # Mensagem BLOCKS <lista_de_blocos>
            parts = decoded.split(maxsplit=1)
            if len(parts) == 2:
                return CMD_BLOCKS, None, parts[1].encode()

        if decoded.startswith(CMD_ERROR):
            # Mensagem ERROR <mensagem>
            parts = decoded.split(maxsplit=1)
            if len(parts) == 2:
                return CMD_ERROR, None, parts[1].encode()

    except Exception as e:
        # Em caso de erro no parsing, retorna comando inválido
        logging.warning(f"Erro ao interpretar mensagem: {e}")
        return CMD_INVALID, None, None

    # Se a mensagem não for reconhecida
    return CMD_UNKNOWN, None, None
