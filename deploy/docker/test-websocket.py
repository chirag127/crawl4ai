#!/usr/bin/env python3
"""
Quick WebSocket test - Connect to monitor WebSocket and print updates
"""

import asyncio
import json

import websockets


async def test_websocket():
    uri = "ws://localhost:11235/monitor/ws"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Receive and print 5 updates
            for i in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"\n📊 Update #{i+1}:")
                print(
                    f"  - Health: CPU {data['health']['container']['cpu_percent']}%, Memory {data['health']['container']['memory_percent']}%"
                )
                print(f"  - Active Requests: {len(data['requests']['active'])}")
                print(f"  - Browsers: {len(data['browsers'])}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    print("\n✅ WebSocket test passed!")
    return 0


if __name__ == "__main__":
    exit(asyncio.run(test_websocket()))
