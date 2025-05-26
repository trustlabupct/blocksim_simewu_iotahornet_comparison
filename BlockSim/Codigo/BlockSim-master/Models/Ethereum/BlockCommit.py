from Scheduler import Scheduler
from InputsConfig import InputsConfig as p
from Models.Ethereum.Node import Node
from Statistics import Statistics
from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
from Models.Network import Network
from Models.Ethereum.Consensus import Consensus as c
from Models.BlockCommit import BlockCommit as BaseBlockCommit


class BlockCommit(BaseBlockCommit):

    @staticmethod
    def handle_event(event):
        """Procesa cualquier tipo de evento: crear bloque o recibir bloque."""
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    @staticmethod
    def generate_block(event):
        """Maneja el evento de creación de bloque."""
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        eventTime = event.time
        blockPrev = event.block.previous

        # Verifica que el nuevo bloque se base en el último bloque minado por este nodo
        if blockPrev == miner.last_block().id:
            # Incrementa el contador de bloques
            Statistics.totalBlocks += 1

            # Incluir transacciones en el bloque
            if p.hasTrans:
                if p.Ttechnique == "Light":
                    blockTrans, blockSize = LT.execute_transactions()
                elif p.Ttechnique == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)

                event.block.transactions = blockTrans
                event.block.usedgas = blockSize

            # Manejo de Uncles (solo Ethereum)
            if p.hasUncles:
                BlockCommit.update_unclechain(miner)
                blockUncles = Node.add_uncles(miner)
                event.block.uncles = blockUncles

            # Agregar el bloque minado a la cadena local
            miner.blockchain.append(event.block)

            # Crear más transacciones (modelo “Light”) si aplica
            if p.hasTrans and p.Ttechnique == "Light":
                LT.create_transactions()

            # Propagar el bloque a otros nodos
            BlockCommit.propagate_block(event.block)

            # Empezar a minar el siguiente bloque
            BlockCommit.generate_next_block(miner, eventTime)

    @staticmethod
    def receive_block(event):
        """Maneja el evento de recepción de un bloque en un nodo."""
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        currentTime = event.time
        blockPrev = event.block.previous

        node = p.NODES[event.node]  # Nodo que recibe el bloque
        lastBlockId = node.last_block().id

        # Caso 1: el bloque recibido se basa en el último bloque de la cadena local
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block)

            # Actualiza el pool de transacciones si es modelo “Full”
            if p.hasTrans and p.Ttechnique == "Full":
                BaseBlockCommit.update_transactionsPool(node, event.block)

            # Minar siguiente bloque en este nodo
            BlockCommit.generate_next_block(node, currentTime)

        else:
            # Profundidad del bloque recibido
            depth = event.block.depth + 1
            # Caso 2: el bloque recibido es más largo que la cadena del nodo => actualizar
            if depth > len(node.blockchain):
                BlockCommit.update_local_blockchain(node, miner, depth)
                BlockCommit.generate_next_block(node, currentTime)
            else:
                # Caso 3: la profundidad no es mayor => el bloque va a la cadena de tíos (uncles)
                uncle = event.block
                node.unclechain.append(uncle)

            # Si existen uncles, depurar la cadena de uncles
            if p.hasUncles:
                BlockCommit.update_unclechain(node)

            # Actualizar transacciones pool (solo “Full”)
            if p.hasTrans and p.Ttechnique == "Full":
                BaseBlockCommit.update_transactionsPool(node, event.block)

    @staticmethod
    def generate_next_block(node, currentTime):
        """Inicia el minado (PoW) del siguiente bloque en un nodo."""
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)
            # Programar el evento de creación del siguiente bloque
            Scheduler.create_block_event(node, blockTime)

    @staticmethod
    def generate_initial_events():
        """Genera eventos de minado inicial para todos los nodos en t=0."""
        currentTime = 0
        for node in p.NODES:
            BlockCommit.generate_next_block(node, currentTime)

    @staticmethod
    def propagate_block(block):
        """Propaga el bloque minado a todos los nodos de la red."""
        for recipient in p.NODES:
            if recipient.id != block.miner:
                blockDelay = Network.block_prop_delay()  
                Scheduler.receive_block_event(recipient, block, blockDelay)

    @staticmethod
    def update_local_blockchain(node, miner, depth):
        """
        Actualiza la cadena local de 'node' para que coincida
        con la de 'miner', cuando se detecta que la del 'miner'
        es más larga.
        """
        i = 0
        while i < depth:
            if i < len(node.blockchain):
                if node.blockchain[i].id != miner.blockchain[i].id:
                    # mover bloque existente a la unclechain
                    node.unclechain.append(node.blockchain[i])
                    newBlock = miner.blockchain[i]
                    node.blockchain[i] = newBlock

                    # actualizar transacciones (si 'Full')
                    if p.hasTrans and p.Ttechnique == "Full":
                        BaseBlockCommit.update_transactionsPool(node, newBlock)
            else:
                # el nodo no tiene este bloque
                newBlock = miner.blockchain[i]
                node.blockchain.append(newBlock)

                if p.hasTrans and p.Ttechnique == "Full":
                    BaseBlockCommit.update_transactionsPool(node, newBlock)

            i += 1

    @staticmethod
    def update_unclechain(node):
        """Elimina duplicados o uncles incluidos en la blockchain."""
        # Quitar duplicados en unclechain
        seen = set()
        x = 0
        while x < len(node.unclechain):
            if node.unclechain[x].id in seen:
                del node.unclechain[x]
                x -= 1
            else:
                seen.add(node.unclechain[x].id)
            x += 1

        # Eliminar uncles que ya están en la blockchain
        j = 0
        while j < len(node.unclechain):
            for blk in node.blockchain:
                if node.unclechain[j].id == blk.id:
                    del node.unclechain[j]
                    j -= 1
                    break
            j += 1

        # Eliminar uncles ya incluidos en algún bloque como uncle
        j = 0
        while j < len(node.unclechain):
            removed = False
            for blk in node.blockchain:
                if hasattr(blk, 'uncles'):
                    for uncle_idx, uncle_blk in enumerate(blk.uncles):
                        if node.unclechain[j].id == uncle_blk.id:
                            del node.unclechain[j]
                            j -= 1
                            removed = True
                            break
                if removed:
                    break
            j += 1
