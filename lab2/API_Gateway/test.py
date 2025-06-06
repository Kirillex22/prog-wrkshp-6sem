import asyncio
import json
from websockets import connect


async def test_subscription():
    uri = "ws://localhost:8080/graphql"
    async with connect(uri, subprotocols=["graphql-transport-ws"]) as websocket:
        # Отправляем connection_init
        await websocket.send(json.dumps({"type": "connection_init", "payload": {}}))

        # Ожидаем подтверждение подключения
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print("Received:", data)

            if data["type"] == "connection_ack":
                # Начинаем подписку после ACK
                subscribe_message = {
                    "id": "1",
                    "type": "subscribe",
                    "payload": {
                        "query": """
                            subscription {
                                transactionAdded {
                                    userid
                                    type
                                    count
                                    timestamp
                                }
                            }
                        """
                    }
                }
                await websocket.send(json.dumps(subscribe_message))

            elif data["type"] == "next":
                # Пришло новое событие подписки
                print("Subscription event:", data["payload"]["data"])

            elif data["type"] == "complete":
                # Сервер завершил подписку
                print("Subscription complete")
                break


asyncio.run(test_subscription())