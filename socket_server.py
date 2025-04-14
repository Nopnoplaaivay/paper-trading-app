from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from src.websocket import TradeData

app = FastAPI()

connected_clients = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client connected:", websocket.client)

    try:
        while True:
            await asyncio.sleep(3)
            stock_infos = TradeData.get_stock_info()
            print(f"Attempting to send data: {stock_infos[0]}")

            # 2. Chuyển đổi dữ liệu thành chuỗi JSON
            try:
                data_to_send = json.dumps(stock_infos)
            except TypeError as e:
                print(f"Error converting data to JSON: {e}. Data was: {stock_infos}")
                continue

            clients_to_remove = []
            for client in connected_clients:
                try:
                    await client.send_text(data_to_send)
                    print(f"✅ Sent data to {client.client}")
                except Exception as send_error:
                    print(f"❌ Error sending to {client.client}: {send_error}")
                    clients_to_remove.append(client)

            # Xóa các client không thể gửi tin nhắn (đã mất kết nối)
            for client in clients_to_remove:
                if client in connected_clients:
                     connected_clients.remove(client)
                     print(f"Removed disconnected client {client.client} during send.")

    except WebSocketDisconnect:
         print(f"Client disconnected gracefully: {websocket.client}")
         if websocket in connected_clients:
             connected_clients.remove(websocket)
    except Exception as e:
        print(f"An unexpected error occurred with {websocket.client}: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


@app.get("/")
async def read_root():
    return {"message": "WebSocket server is running"}