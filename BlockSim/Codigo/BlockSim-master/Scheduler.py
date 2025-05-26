from InputsConfig import InputsConfig as p
import random
from Models.Block import Block
from Event import Event, Queue

if p.model == 2:
    from Models.Ethereum.Block import Block
elif p.model == 3:
    from Models.AppendableBlock.Block import Block as AB
    from Models.AppendableBlock.Node import Node
else:
    from Models.Block import Block


class Scheduler:

    @staticmethod
    def create_block_event(miner, eventTime):
        eventType = "create_block"
        if eventTime <= p.simTime:
            # prepare attributes for the event
            block = Block()
            block.miner = miner.id
            block.depth = len(miner.blockchain)
            block.id = random.randrange(100000000000)
            block.previous = miner.last_block().id
            block.timestamp = eventTime

            event = Event(eventType, block.miner, eventTime, block)

            print(f"[Scheduler] create_block_event -> "
                  f"Se agenda evento='{eventType}', "
                  f"t={eventTime}, "
                  f"minerId={block.miner}, "
                  f"blockId={block.id}, "
                  f"blockDepth={block.depth}")

            Queue.add_event(event)
        else:
            print(f"[Scheduler] create_block_event -> Evento no agendado, "
                  f"eventTime={eventTime} supera simTime={p.simTime}")

    @staticmethod
    def receive_block_event(recipient, block, blockDelay):
        receive_block_time = block.timestamp + blockDelay
        if receive_block_time <= p.simTime:
            e = Event("receive_block", recipient.id, receive_block_time, block)

            print(f"[Scheduler] receive_block_event -> "
                  f"Se agenda evento='receive_block', "
                  f"t={receive_block_time}, "
                  f"recipientId={recipient.id}, "
                  f"blockId={block.id}")

            Queue.add_event(e)
        else:
            print(f"[Scheduler] receive_block_event -> Evento no agendado, "
                  f"t={receive_block_time} supera simTime={p.simTime}")

    @staticmethod
    def create_block_event_AB(node, eventTime, receiverGatewayId):
        eventType = "create_block"
        if eventTime <= p.simTime:
            block = AB()
            block.id = random.randrange(100000000000)
            block.timestamp = eventTime
            block.nodeId = node.id
            block.gatewayIds = node.gatewayIds
            block.receiverGatewayId = receiverGatewayId

            event = Event(eventType, node.id, eventTime, block)

            print(f"[Scheduler] create_block_event_AB -> "
                  f"Se agenda evento='{eventType}', "
                  f"t={eventTime}, "
                  f"nodeId={node.id}, "
                  f"blockId={block.id}, "
                  f"destGateway={receiverGatewayId}")

            Queue.add_event(event)
        else:
            print(f"[Scheduler] create_block_event_AB -> "
                  f"Evento no agendado, eventTime={eventTime} supera simTime={p.simTime}")

    @staticmethod
    def append_tx_list_event(txList, gatewayId, tokenTime, eventTime):
        eventType = "append_tx_list"
        if eventTime <= p.simTime:
            block = AB()
            block.transactions = txList.copy()
            block.timestamp = tokenTime

            event = Event(eventType, gatewayId, eventTime, block)

            print(f"[Scheduler] append_tx_list_event -> "
                  f"Se agenda evento='{eventType}', "
                  f"t={eventTime}, "
                  f"gatewayId={gatewayId}, "
                  f"numTx={len(txList)}")

            Queue.add_event(event)
        else:
            print(f"[Scheduler] append_tx_list_event -> "
                  f"Evento no agendado, eventTime={eventTime} supera simTime={p.simTime}")

    @staticmethod
    def receive_tx_list_event(txList, gatewayId, tokenTime, eventTime):
        eventType = "receive_tx_list"
        if eventTime <= p.simTime:
            block = AB()
            block.transactions = txList.copy()
            block.timestamp = tokenTime

            event = Event(eventType, gatewayId, eventTime, block)

            print(f"[Scheduler] receive_tx_list_event -> "
                  f"Se agenda evento='{eventType}', "
                  f"t={eventTime}, "
                  f"gatewayId={gatewayId}, "
                  f"numTx={len(txList)}")

            Queue.add_event(event)
        else:
            print(f"[Scheduler] receive_tx_list_event -> "
                  f"Evento no agendado, eventTime={eventTime} supera simTime={p.simTime}")
