from InputsConfig import InputsConfig as p
from Event import Event, Queue
from Scheduler import Scheduler
from Statistics import Statistics
from datetime import datetime

if p.model == 3:
    from Models.AppendableBlock.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.AppendableBlock.Transaction import FullTransaction as FT
    from Models.AppendableBlock.Node import Node
    from Models.Incentives import Incentives
    from Models.AppendableBlock.Statistics import Statistics
    from Models.AppendableBlock.Verification import Verification

elif p.model == 2:
    from Models.Ethereum.BlockCommit import BlockCommit
    from Models.Ethereum.Consensus import Consensus
    from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Ethereum.Node import Node
    from Models.Ethereum.Incentives import Incentives

elif p.model == 1:
    from Models.Bitcoin.BlockCommit import BlockCommit
    from Models.Bitcoin.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Bitcoin.Node import Node
    from Models.Incentives import Incentives

elif p.model == 0:
    from Models.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Node import Node
    from Models.Incentives import Incentives


########################################################## Start Simulation ##############################################################

def main():
    print(f"[MAIN] Iniciando la simulación con p.model={p.model}")
    print(f"[MAIN] Número de corridas (Runs)={p.Runs}, simTime={p.simTime}")

    for i in range(p.Runs):
        print(f"\n[MAIN] === RUN {i+1} de {p.Runs} ===")
        clock = 0  # set clock to 0 at the start of the simulation
        print(f"[MAIN] Reloj de simulación reiniciado a {clock}")

        if p.hasTrans:
            print(f"[MAIN] p.hasTrans = True, generando transacciones con técnica={p.Ttechnique}")
            if p.Ttechnique == "Light":
                LT.create_transactions()  # generate pending transactions
            elif p.Ttechnique == "Full":
                FT.create_transactions()  # generate pending transactions
        else:
            print("[MAIN] p.hasTrans = False, no se generarán transacciones")

        print("[MAIN] Generando bloque génesis para todos los nodos...")
        Node.generate_gensis_block()

        print("[MAIN] Generando eventos iniciales (arranque del minado)...")
        BlockCommit.generate_initial_events()

        print(f"[MAIN] Iniciando bucle principal de eventos (hasta simTime={p.simTime})...")
        while not Queue.isEmpty() and clock <= p.simTime:
            next_event = Queue.get_next_event()
            clock = next_event.time  # move clock to the time of the event

            print(f"[MAIN] - Procesando evento (type={next_event.type}) en t={clock} (Queue size={Queue.size()})")

            BlockCommit.handle_event(next_event)

            # En caso de querer ver más detalle del evento (nodo, bloque, etc.), añade aquí más prints:
            # e.g. print(f"[MAIN]   Evento en nodo={next_event.node}, blockId={next_event.block.id}")

            Queue.remove_event(next_event)

        print(f"[MAIN] - Bucle de eventos finalizado. (Queue empty? {Queue.isEmpty()}  clock={clock})")

        # for the AppendableBlock process transactions and optionally verify the model implementation
        if p.model == 3:
            print("[MAIN] Modo AppendableBlock: procesando transaction pools y verificación si aplica...")
            BlockCommit.process_gateway_transaction_pools()

            if i == 0 and p.VerifyImplemetation:
                print("[MAIN] Verificando la implementación en la primera corrida...")
                Verification.perform_checks()

        print("[MAIN] Resolviendo forks (fork_resolution)...")
        Consensus.fork_resolution()

        print("[MAIN] Distribuyendo recompensas (distribute_rewards)...")
        Incentives.distribute_rewards()

        print("[MAIN] Calculando estadísticas de la simulación (Statistics.calculate())...")
        Statistics.calculate()

        if p.model == 3:
            print("[MAIN] Guardando resultados en Excel (AppendableBlock)...")
            Statistics.print_to_excel(i, True)
            Statistics.reset()
        else:
            print("[MAIN] Guardando resultados en Excel (modo base, Bitcoin o Ethereum)...")
            Statistics.reset()
            Node.resetState()
            fname = "(Allverify)1day_{0}M_{1}K.xlsx".format(
                p.Bsize/1000000, p.Tn/1000)
            Statistics.print_to_excel(fname)

    ahora = datetime.now()
    hora_formateada = ahora.strftime("%H:%M:%S.") + f"{int(ahora.microsecond / 1000):03d}"
    print("Hora de finalización:", hora_formateada)
    print("\n[MAIN] Simulación completa. Saliendo...")

######################################################## Run Main method #####################################################################
if __name__ == '__main__':
    # Se imprime el modelo al inicio (ya lo hace la línea de debug):
    # print(p.model)
    ahora = datetime.now()
    hora_formateada = ahora.strftime("%H:%M:%S.") + f"{int(ahora.microsecond / 1000):03d}"
    print("Hora actual:", hora_formateada)
    main()

