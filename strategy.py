import random
import logging
from typing import Dict, Set, List

def select_rarest_blocks(peer_block_map: Dict[str, Set[int]], my_blocks: Set[int]) -> List[int]:
    """
    Estratégia Rarest First: prioriza os blocos menos comuns entre os peers disponíveis.

    Args:
        peer_block_map (dict): Mapeamento peer -> blocos disponíveis
        my_blocks (set): Blocos já presentes no peer atual

    Returns:
        list: Lista ordenada dos blocos mais raros para os mais comuns
    """
    block_frequency = {}

    # Conta a frequência de cada bloco entre os peers, ignorando os que o peer atual já tem
    for blocks in peer_block_map.values():
        for block in blocks:
            if block not in my_blocks:
                block_frequency[block] = block_frequency.get(block, 0) + 1

    # Retorna os blocos ordenados do mais raro para o mais comum
    return sorted(block_frequency.keys(), key=lambda b: block_frequency[b])

class Strategy:
    def __init__(self):
        # Lista de peers desbloqueados fixos (até 4)
        self.regular_unchoked: List[str] = []
        # Peer desbloqueado aleatoriamente (optimistic unchoke)
        self.optimistic_peer: str = ""

    def update_unchoked_peers(self, known_peers: List[str], peer_block_map: Dict[str, Set[int]], my_blocks: Set[int]):
        """
        Atualiza os peers desbloqueados com base na utilidade (tit-for-tat + unchoke otimista).

        Args:
            known_peers (list): Lista de peers conhecidos (formato "IP:porta")
            peer_block_map (dict): Mapeamento peer -> blocos disponíveis
            my_blocks (set): Blocos já baixados
        """
        # Calcula quantos blocos úteis cada peer possui (ou seja, blocos que eu ainda não tenho)
        scored_peers = []
        for peer, blocks in peer_block_map.items():
            useful_blocks = len(blocks - my_blocks)
            scored_peers.append((peer, useful_blocks))

        # Ordena os peers pelo número de blocos úteis (decrescente)
        scored_peers.sort(key=lambda x: x[1], reverse=True)

        # Seleciona os 4 mais úteis como peers desbloqueados fixos
        self.regular_unchoked = [peer for peer, _ in scored_peers[:4]]

        # Escolhe aleatoriamente 1 peer entre os restantes como desbloqueado otimista
        candidates = [peer for peer in known_peers if peer not in self.regular_unchoked]
        self.optimistic_peer = random.choice(candidates) if candidates else ""

        # Loga os peers desbloqueados para monitoramento
        logging.info(f"Unchoked peers: {self.regular_unchoked}")
        if self.optimistic_peer:
            logging.info(f"Optimistic unchoke: {self.optimistic_peer}")

    def get_unchoked_peers(self) -> List[str]:
        """
        Retorna todos os peers desbloqueados (fixos + otimista).
        """
        return self.regular_unchoked + ([self.optimistic_peer] if self.optimistic_peer else [])

    def should_request_from(self, peer_id: str) -> bool:
        """
        Verifica se o peer remoto está atualmente desbloqueado.
        """
        return peer_id in self.get_unchoked_peers()
