import numpy as np
from InputsConfig import InputsConfig as p
from Models.Node import Node
import random
import pandas as pd
from Models.Consensus import Consensus as c

class Statistics:

    # Variables usadas para almacenar datos de la simulación
    totalBlocks = 0
    mainBlocks  = 0
    totalUncles = 0
    uncleBlocks = 0
    staleBlocks = 0
    uncleRate   = 0
    staleRate   = 0
    blockData   = []
    blocksResults = []
    # profits: cada fila corresponde a un minero en un run
    # (N miners * R runs) filas, con 7 columnas
    profits = [[0 for x in range(7)] for y in range(p.Runs * len(p.NODES))]
    index = 0
    chain = []

    @staticmethod
    def calculate():
        print("[Statistics.calculate] -> Iniciando cálculo de estadísticas")
        Statistics.global_chain()   # Prepara la global chain
        Statistics.blocks_results() # Calcula métricas de bloques (# main, # stale, # uncles, etc.)
        Statistics.profit_results() # Calcula recompensas y populates 'profits'

    @staticmethod
    def blocks_results():
        """
        Calcula y guarda estadísticas sobre los bloques minados:
        - mainBlocks
        - staleBlocks
        - uncleBlocks (Ethereum)
        - transacciones totales, etc.
        """
        print("[Statistics.blocks_results] -> Calculando estadísticas de bloques")
        trans = 0

        # El primer bloque en c.global_chain suele ser el Génesis (depende de tu implementación)
        Statistics.mainBlocks = len(c.global_chain) - 1
        Statistics.staleBlocks = Statistics.totalBlocks - Statistics.mainBlocks

        for b in c.global_chain:
            if p.model == 2:
                Statistics.uncleBlocks += len(b.uncles)
            else:
                Statistics.uncleBlocks = 0
            trans += len(b.transactions)

        Statistics.staleRate = round(Statistics.staleBlocks / Statistics.totalBlocks * 100, 2) if Statistics.totalBlocks > 0 else 0
        if p.model == 2:
            Statistics.uncleRate = round(Statistics.uncleBlocks / Statistics.totalBlocks * 100, 2) if Statistics.totalBlocks > 0 else 0
        else:
            Statistics.uncleRate = 0

        Statistics.blockData = [
            Statistics.totalBlocks,
            Statistics.mainBlocks,
            Statistics.uncleBlocks,
            Statistics.uncleRate,
            Statistics.staleBlocks,
            Statistics.staleRate,
            trans
        ]

        Statistics.blocksResults.append(Statistics.blockData)

        print(f"[Statistics.blocks_results] -> totalBlocks={Statistics.totalBlocks}, "
              f"mainBlocks={Statistics.mainBlocks}, "
              f"staleBlocks={Statistics.staleBlocks}, "
              f"uncleBlocks={Statistics.uncleBlocks}, "
              f"uncleRate={Statistics.uncleRate}%, "
              f"staleRate={Statistics.staleRate}%, "
              f"transactions={trans}"
        )

    @staticmethod
    def profit_results():
        """
        Calcula y llena la matriz 'profits' con:
          - ID de minero
          - % hash power
          - # bloques minados
          - % de main blocks
          - # uncle blocks (Ethereum)
          - % de uncles (Ethereum)
          - balance (recompensa)
        """
        print("[Statistics.profit_results] -> Calculando recompensas/profit para cada nodo")

        for m in p.NODES:
            i = Statistics.index + m.id * p.Runs
            Statistics.profits[i][0] = m.id
            if p.model == 0:
                Statistics.profits[i][1] = "NA"
            else:
                Statistics.profits[i][1] = m.hashPower

            Statistics.profits[i][2] = m.blocks
            # Evitar división entre cero si mainBlocks=0
            if Statistics.mainBlocks > 0:
                Statistics.profits[i][3] = round(m.blocks / Statistics.mainBlocks * 100, 2)
            else:
                Statistics.profits[i][3] = 0

            if p.model == 2:
                Statistics.profits[i][4] = m.uncles
                # Evitar división cero si mainBlocks + totalUncles=0
                denom = (Statistics.mainBlocks + Statistics.totalUncles) if (Statistics.mainBlocks + Statistics.totalUncles) else 1
                Statistics.profits[i][5] = round((m.blocks + m.uncles)/denom * 100, 2)
            else:
                Statistics.profits[i][4] = 0
                Statistics.profits[i][5] = 0

            Statistics.profits[i][6] = m.balance

            print(f"[Statistics.profit_results] -> Nodo={m.id}: blocks={m.blocks}, uncles={getattr(m, 'uncles', 0)}, balance={m.balance}")

        Statistics.index += 1

    @staticmethod
    def global_chain():
        """
        Construye 'Statistics.chain' con info de cada bloque de la
        cadena global (c.global_chain). En Ethereum (p.model=2),
        agrega info de 'usedgas' y # uncles.
        """
        print("[Statistics.global_chain] -> Preparando la global chain para análisis")

        if p.model in (0, 1):
            for i in c.global_chain:
                block = [
                    i.depth,
                    i.id,
                    i.previous,
                    i.timestamp,
                    i.miner,
                    len(i.transactions),
                    i.size
                ]
                Statistics.chain.append(block)

        elif p.model == 2:
            for i in c.global_chain:
                block = [
                    i.depth,
                    i.id,
                    i.previous,
                    i.timestamp,
                    i.miner,
                    len(i.transactions),
                    i.usedgas,
                    len(i.uncles)
                ]
                Statistics.chain.append(block)

    @staticmethod
    def print_to_excel(fname):
        """
        Exporta datos de configuración y resultados a un archivo .xlsx
        - df1: Configuración de entrada
        - df2: Resultados de bloques (stale rate, uncle rate, etc.)
        - df3: Tabla de recompensas por minero
        - df4: Detalle de la cadena global
        """
        print(f"[Statistics.print_to_excel] -> Guardando resultados en {fname}...")

        df1 = pd.DataFrame({
            'Block Time': [p.Binterval],
            'Block Propagation Delay': [p.Bdelay],
            'No. Miners': [len(p.NODES)],
            'Simulation Time': [p.simTime]
        })

        df2 = pd.DataFrame(Statistics.blocksResults)
        df2.columns = [
            'Total Blocks',
            'Main Blocks',
            'Uncle blocks',
            'Uncle Rate',
            'Stale Blocks',
            'Stale Rate',
            '# transactions'
        ]

        df3 = pd.DataFrame(Statistics.profits)
        df3.columns = [
            'Miner ID',
            '% Hash Power',
            '# Mined Blocks',
            '% of main blocks',
            '# Uncle Blocks',
            '% of uncles',
            'Profit (in ETH)'
        ]

        df4 = pd.DataFrame(Statistics.chain)
        if p.model == 2:
            df4.columns = [
                'Block Depth',
                'Block ID',
                'Previous Block',
                'Block Timestamp',
                'Miner ID',
                '# transactions',
                'Block Limit',
                'Uncle Blocks'
            ]
        else:
            df4.columns = [
                'Block Depth',
                'Block ID',
                'Previous Block',
                'Block Timestamp',
                'Miner ID',
                '# transactions',
                'Block Size'
            ]

        writer = pd.ExcelWriter(fname, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='InputConfig', index=False)
        df2.to_excel(writer, sheet_name='SimOutput', index=False)
        df3.to_excel(writer, sheet_name='Profit',    index=False)
        df4.to_excel(writer, sheet_name='Chain',     index=False)

        writer.close()
        print("[Statistics.print_to_excel] -> Resultados guardados con éxito.")

    @staticmethod
    def reset():
        """
        Reset de variables globales para la siguiente corrida o para limpiar antes de otra simulación
        """
        print("[Statistics.reset] -> Limpiando estadísticas principales")
        Statistics.totalBlocks   = 0
        Statistics.totalUncles   = 0
        Statistics.mainBlocks    = 0
        Statistics.uncleBlocks   = 0
        Statistics.staleBlocks   = 0
        Statistics.uncleRate     = 0
        Statistics.staleRate     = 0
        Statistics.blockData     = []

    @staticmethod
    def reset2():
        """
        Reset de blocksResults, profits, index y la cadena
        """
        print("[Statistics.reset2] -> Limpiando blocksResults, profits, index, chain")
        Statistics.blocksResults = []
        Statistics.profits       = [[0 for x in range(7)] for y in range(p.Runs * len(p.NODES))]
        Statistics.index         = 0
        Statistics.chain         = []
