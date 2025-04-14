import json
import asyncio
import websockets

async def test_websocket_client():
    uri = "ws://localhost:8000/ws"  # URL WebSocket của bạn
    print("Connecting to WebSocket server at", uri)
    async with websockets.connect(uri) as websocket:
        while True:
            res = await websocket.recv()  # Nhận dữ liệu từ server
            print("Received from server:", res)
            print(type(res))

            # Kiểm tra dữ liệu
            try:
                json_data = json.loads(res)
                print("Data is valid JSON:", json_data[0])
            except json.JSONDecodeError:
                print("Data is not valid JSON")

if __name__ == "__main__":
    asyncio.run(test_websocket_client())