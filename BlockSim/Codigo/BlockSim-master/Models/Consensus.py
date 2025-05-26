import numpy as np
from InputsConfig import InputsConfig as p
from Models.Node import Node
import random

class Consensus:
    # la cadena aceptada globalmente tras resolver forks
    global_chain = []

    @staticmethod
    def Protocol(node):
        """
        Modela la lógica del protocolo de consenso, por ejemplo
        el tiempo de minado (PoW). Aquí puedes usar la hashPower
        del nodo y alguna distribución estadística para calcular
        el tiempo de bloque.
        """
        # Ejemplo de un modelo muy simple: tiempo de bloque exponencial en función de hashPower:
        # blockTime = np.random.exponential(1 / node.hashPower)  # Ajustar según tu modelo
        # Para no romper tu lógica, lo dejamos sin cálculo real:
        # blockTime = ...
        
        print(f"[Consensus.Protocol] Calculando tiempo de minado para nodo={node.id} con hashPower={node.hashPower}")
        
        # Aquí un ejemplo de dummy:
        blockTime = random.expovariate(node.hashPower * 0.001)  # Ajusta a tu gusto
        print(f"[Consensus.Protocol] Tiempo de bloque calculado={blockTime:.4f} s (aprox) para nodo={node.id}")
        
        return blockTime

    @staticmethod
    def fork_resolution():
        """
        Método para resolver forks en la red. Se recorre la blockchain de cada nodo
        para elegir la cadena 'ganadora' (por ejemplo, la más larga) y se establece
        en global_chain.
        """
        print("[Consensus.fork_resolution] Iniciando resolución de forks...")

        # EJEMPLO de lógica muy simplificada:
        # 1. Revisar todos los nodos, encontrar la blockchain más larga
        # 2. Asignarla a global_chain
        # 3. Cada nodo actualiza su cadena a la global
        max_length = 0
        winning_chain = None
        
        for node in p.NODES:
            chain_len = len(node.blockchain)
            print(f"[Consensus.fork_resolution] Nodo={node.id} tiene cadena de longitud={chain_len}")
            if chain_len > max_length:
                max_length = chain_len
                winning_chain = node.blockchain

        if winning_chain:
            # Copiamos la referencia o clonamos según tu lógica
            Consensus.global_chain = winning_chain
            print(f"[Consensus.fork_resolution] Cadena ganadora de longitud={max_length}. Actualizando nodos...")

            # Actualizar todos los nodos a la cadena ganadora
            for node in p.NODES:
                if len(node.blockchain) < max_length:
                    node.blockchain = list(winning_chain)  # o la referencia que necesites
                    print(f"[Consensus.fork_resolution] Nodo={node.id} sincronizado con cadena de longitud={max_length}")

        print("[Consensus.fork_resolution] Fork resolution finalizada. "
              f"Longitud de la global_chain={len(Consensus.global_chain)}")
