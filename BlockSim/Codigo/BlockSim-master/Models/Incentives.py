from InputsConfig import InputsConfig as p
from Models.Consensus import Consensus as c

class Incentives:

    """
     Defines the rewarded elements (block + transactions), calculate and distribute
     the rewards among the participating nodes
    """
    @staticmethod
    def distribute_rewards():
        print("[Incentives.distribute_rewards] -> Repartiendo recompensas a los nodos...")

        # Recorremos cada bloque de la cadena global para asignar recompensas al minero
        for bc in c.global_chain:
            for m in p.NODES:
                if bc.miner == m.id:
                    m.blocks += 1
                    # Aumentamos el balance del minero por la recompensa base de bloque
                    m.balance += p.Breward

                    # Calculamos comisiones totales de transacciones en el bloque
                    tx_fee = Incentives.transactions_fee(bc)
                    m.balance += tx_fee

                    print(f"[Incentives.distribute_rewards] Nodo={m.id} minó el bloque ID={bc.id}, "
                          f"total bloques minados={m.blocks}, "
                          f"reward={p.Breward}, tx_fee={tx_fee}, nuevo balance={m.balance}")

    @staticmethod
    def transactions_fee(bc):
        """
        Suma las comisiones de todas las transacciones incluidas en el bloque `bc`.
        """
        fee = 0
        for tx in bc.transactions:
            fee += tx.fee
        # Para ver cuántas transacciones y la comisión total del bloque:
        print(f"[Incentives.transactions_fee] Bloque ID={bc.id}, #transacciones={len(bc.transactions)}, fee total={fee}")
        return fee
