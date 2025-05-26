from Scheduler import Scheduler
from InputsConfig import InputsConfig as p
from Models.Bitcoin.Node import Node
from Statistics import Statistics
from Models.Transaction import LightTransaction as LT, FullTransaction as FT
from Models.Network import Network
from Models.Bitcoin.Consensus import Consensus as c
from Models.BlockCommit import BlockCommit as BaseBlockCommit

class BlockCommit(BaseBlockCommit):

    # Manejo y ejecución de eventos
    def handle_event(event):
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Evento de creación de bloque
    def generate_block(event):
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        eventTime = event.time
        blockPrev = event.block.previous

        # Verificar que el bloque previo coincida con el último de la cadena local
        if blockPrev == miner.last_block().id:
            Statistics.totalBlocks += 1  # Incrementar el conteo global de bloques creados

            # Manejo de transacciones (si está habilitado)
            if p.hasTrans:
                if p.Ttechnique == "Light":
                    blockTrans, blockSize = LT.execute_transactions()
                elif p.Ttechnique == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)

                event.block.transactions = blockTrans
                event.block.usedgas = blockSize

            # Añadir bloque a la cadena local de este minero
            miner.blockchain.append(event.block)

            # Si es técnica Light, generar nuevas transacciones tras minar
            if p.hasTrans and p.Ttechnique == "Light":
                LT.create_transactions()

            # Propagar el nuevo bloque y generar el siguiente evento de minado
            BlockCommit.propagate_block(event.block)
            BlockCommit.generate_next_block(miner, eventTime)

    # Evento de recepción de bloque
    def receive_block(event):
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        currentTime = event.time
        blockPrev = event.block.previous  # ID del bloque previo

        node = p.NODES[event.node]  # Nodo que recibe el bloque
        lastBlockId = node.last_block().id  # ID del último bloque en la cadena local

        # Caso 1: el bloque recibido se basa en el último bloque de la cadena local
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block)
            if p.hasTrans and p.Ttechnique == "Full":
                BlockCommit.update_transactionsPool(node, event.block)

            # Iniciar minado para el siguiente bloque
            BlockCommit.generate_next_block(node, currentTime)

        # Caso 2: el bloque no se construye sobre el último bloque local (posible fork)
        else:
            depth = event.block.depth + 1
            if depth > len(node.blockchain):
                BlockCommit.update_local_blockchain(node, miner, depth)
                BlockCommit.generate_next_block(node, currentTime)

            if p.hasTrans and p.Ttechnique == "Full":
                BlockCommit.update_transactionsPool(node, event.block)

    # Al generar/recibir un bloque, se programa la minería del siguiente
    def generate_next_block(node, currentTime):
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)  # Tiempo estimado para minar el siguiente bloque
            Scheduler.create_block_event(node, blockTime)

    # Generar los eventos iniciales de minado (uno por nodo) al inicio
    def generate_initial_events():
        currentTime = 0
        for node in p.NODES:
            BlockCommit.generate_next_block(node, currentTime)

    # Propagar un bloque recién minado a todos los demás nodos
    def propagate_block(block):
        for recipient in p.NODES:
            if recipient.id != block.miner:
                # Retraso de propagación (puede ser 0 o tomado de una distribución)
                blockDelay = Network.block_prop_delay()
                Scheduler.receive_block_event(recipient, block, blockDelay)

    # Actualiza la cadena local de 'node' en caso de fork o de recibir un bloque más largo
    # (Ejemplo placeholder; depende de tu lógica concreta)
    def update_local_blockchain(node, miner, depth):
        pass

    # Actualiza el pool de transacciones al recibir un bloque (placeholder)
    def update_transactionsPool(node, block):
        pass
