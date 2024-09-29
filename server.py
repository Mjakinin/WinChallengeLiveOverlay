import asyncio
import websockets

# Die aktuelle Checkliste - alle Clients teilen sich diese Liste
checklist = [0] * 10  # 10 Tasks, alle standardmäßig nicht angekreuzt (0 = nicht angekreuzt)

# Verbundene Clients
connected_clients = set()

async def handler(websocket):
    global checklist  # Die globale Variable checklist wird hier deklariert
    # Füge den Client zur Liste der verbundenen Clients hinzu
    connected_clients.add(websocket)
    
    # Sende dem neuen Client die aktuelle Checkliste
    await websocket.send(str(checklist))

    try:
        async for message in websocket:
            # Empfange die neuen Checklisten-Daten vom Client
            changes = eval(message)
            
            # Aktualisiere die globale Checkliste
            checklist = changes

            # Sende die aktualisierte Checkliste an alle verbundenen Clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(str(checklist))
    
    except websockets.ConnectionClosed:
        pass
    
    finally:
        # Entferne den Client, wenn die Verbindung geschlossen wird
        connected_clients.remove(websocket)

async def main():
    # Starte den WebSocket-Server auf Port 8765
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # läuft unendlich

# Startet den Server
asyncio.run(main())
