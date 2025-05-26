from InputsConfig import InputsConfig as p

class BlockCommit:

    # Handling and running Events
    def handle_event(event):
        print(f"[BlockCommit.handle_event] -> Recibido evento de tipo='{event.type}'")
        # Podrías mostrar más atributos si existen, por ej: 
        # print(f"[BlockCommit.handle_event]    event.time={event.time}, node={event.node}, blockId={event.block.id}")

        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Block Creation Event
    def generate_block(event):
        """
        Aquí se crea un bloque nuevo. Ejemplo de prints para saber:
        - Quién mina
        - ID del nuevo bloque
        - Tiempo del evento
        """
        print(f"[BlockCommit.generate_block] -> Creando bloque en tiempo={getattr(event, 'time', None)}")
        # Si event.block existe y contiene info del minero:
        #   print(f"[BlockCommit.generate_block]    Minero={event.block.miner}, Bloque ID={event.block.id}")

        # ... aquí va tu lógica original (POW, añadir transacciones, etc.) ...
        pass

    # Block Receiving Event
    def receive_block(event):
        """
        Este método se llama cuando un nodo recibe un bloque minado por otro nodo.
        """
        print(f"[BlockCommit.receive_block] -> Nodo={getattr(event, 'node', None)} recibe bloque")
        # Podrías mostrar ID del bloque recibido y minero original:
        #   print(f"[BlockCommit.receive
