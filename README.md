
# Projeto P2P Inspirado no BitTorrent

Este projeto simula uma rede P2P (peer-to-peer) local que distribui um arquivo dividido em blocos entre múltiplos peers, utilizando estratégias como Rarest First e Tit-for-Tat simplificado, com a coordenação de um servidor Tracker central.

O projeto segue os princípios do BitTorrent, com as seguintes características:

---

### Funcionalidades implementadas:

1. **Divisão do arquivo em blocos**
   - Um arquivo `.txt` é dividido em blocos de tamanho configurável (padrão: 1024 bytes).
   - Os blocos são salvos como arquivos `block_0.bin`, `block_1.bin`, ..., numerados e identificáveis.

2. **Distribuição inicial entre peers**
   - Cada peer recebe um subconjunto aleatório dos blocos ao ser inicializado pela função `split_and_distribute`.

3. **Comunicação peer-to-peer (P2P)**
   - Cada peer possui um servidor próprio e um cliente que solicita blocos aos demais peers.

4. **Uso de um Tracker**
   - Um servidor central simples (`tracker_server.py`) que mantém a lista de peers ativos.
   - Ao ser consultado, retorna um subconjunto aleatório dos peers, exceto quem consultou.

5. **Algoritmo "Rarest First"**
   - Os peers priorizam blocos menos comuns na rede para balancear a distribuição.

6. **Algoritmo "Olho por olho" (Tit-for-Tat simplificado)**
   - A cada 10 segundos, o peer atualiza sua lista de "unchoked" peers (desbloqueados).
   - São escolhidos até 4 peers úteis e 1 otimista (aleatório).
   - Peers úteis são aqueles com maior quantidade de blocos raros.

7. **Encerramento controlado**
   - Um peer só finaliza o processo quando possuir todos os blocos e consegue reconstruir o arquivo.
   - Após reconstruir, ele continua ‘online’ como seeder para ajudar outros peers.

---

## Estrutura de Arquivos

```
minibit/
├── file_manager.py
├── peer.py
├── peer_client.py
├── peer_server.py
├── protocol.py
├── strategy.py
├── tracker_server.py
├── tracker_client.py
├── launcher.py
├── historia.txt
├── README.md
├── peers/
│   ├── blocks/
│   ├── peer_1/
│   ├── peer_n/
├── reconstruidos/
└── scripts/
    ├── unix/
    │   ├── start_tracker.sh
    │   ├── start_peers.sh
    │   ├── stop_all.sh
    │   └── cleanup.sh
    └── windows/
        ├── start_tracker.ps1
        ├── start_peers.ps1
        ├── stop_all.ps1
        └── cleanup.ps1
```

---

## Como Executar o Projeto (independente do SO)

### 1. Preparar o arquivo a ser distribuído

```bash
python -c "from file_manager import split_and_distribute; split_and_distribute('seuarquivo.txt')"
```

> **Observação:** Caso deseje alterar o número de peers ou o tamanho do bloco (block size), edite as variáveis `NUM_PEERS` e `BLOCK_SIZE` no arquivo `file_manager.py` antes de rodar o comando acima.

---

### 2. Rodar o Tracker

> O tracker deve ser iniciado em uma **aba/terminal separado**, pois ele ficará escutando conexões enquanto os peers se comunicam.

```bash
python launcher.py start_tracker
```

---

### 3. Rodar os Peers

```bash
python launcher.py start_peers
```

---

### 4. Parar todos os Peers e o Tracker

```bash
python launcher.py stop_all
```

---

### 5. Reiniciar o Projeto com Outro Arquivo

```bash
python launcher.py cleanup
python -c "from file_manager import split_and_distribute; split_and_distribute('NOVO_ARQUIVO.txt')"
```

---

## Observações Finais

- O sistema continua a rodar após a reconstrução do arquivo para simular o comportamento de seeders.
- Os logs informam:
  - Quais blocos o peer possui em cada momento;
  - Quais peers estão desbloqueados (unchoked);
  - Quando o arquivo foi reconstruído com sucesso;
  - O comportamento da estratégia Tit-for-Tat a cada 10 segundos.


Repositório no GitHub

Acesse o código-fonte completo do projeto no repositório: https://github.com/ViniMattias/MiniBit

