import asyncio
import websockets
import os
import json

# এখানে সব "রুম" (pairing code) এর তথ্য জমা থাকবে
rooms = {}


async def handler(websocket):
    room_code = None
    try:
        # প্রথম মেসেজেই ক্লায়েন্ট তার pairing code পাঠাবে
        first_message = await websocket.recv()
        data = json.loads(first_message)
        room_code = data.get("room")

        if not room_code:
            await websocket.close()
            return

        if room_code not in rooms:
            rooms[room_code] = []
        rooms[room_code].append(websocket)

        print(f"একজন client যুক্ত হলো room: {room_code} (মোট: {len(rooms[room_code])})")

        # এরপর থেকে যা মেসেজ আসবে, একই রুমের অন্য PC-তে পাঠিয়ে দেবে
        async for message in websocket:
            for client in rooms[room_code]:
                if client != websocket:
                    await client.send(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room_code and room_code in rooms and websocket in rooms[room_code]:
            rooms[room_code].remove(websocket)
            if not rooms[room_code]:
                del rooms[room_code]
            print(f"একজন client বের হয়ে গেলো room: {room_code}")


async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"Relay server চালু আছে, port: {port}")
        await asyncio.Future()  # চিরকাল চালু থাকবে


if __name__ == "__main__":
    asyncio.run(main())
