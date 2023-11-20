class WebSocketManager:
    def __init__(self):
        self.web_clients = set()

    async def register(self, websocket, data):
        self.web_clients.add(websocket)

    async def unregister(self, websocket):
        self.web_clients.remove(websocket)

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)