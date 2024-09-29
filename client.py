import tkinter as tk
import asyncio
import websockets
import threading
import json
import os

class Overlay:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Entfernt die Titelleiste
        self.root.attributes("-topmost", True)  # Fenster immer im Vordergrund
        self.root.geometry("300x420")  # Größe des Fensters

        # Berechnung der Position für das mittige Platzieren
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (300 // 2)  # x-Position
        y = (screen_height // 2) - (420 // 2)  # y-Position
        self.root.geometry(f"300x420+{x}+{y}")  # Position mittig

        self.root.configure(bg="#1A1A1A")  # Dunkelgrauer Hintergrund für den Eindruck von Deckkraft
        
        # Überschrift "Winchallenge"
        self.title = tk.Label(self.root, text="Winchallenge", font=("Comic Sans MS", 16, "bold"), bg="#1A1A1A", fg="#FFFFFF")
        self.title.pack(pady=10)
        
        # Binde Maus-Events an die Überschrift für das Verschieben
        self.title.bind("<ButtonPress-1>", self.start_drag)
        self.title.bind("<ButtonRelease-1>", self.stop_drag)
        self.title.bind("<B1-Motion>", self.drag)

        # Liste der Challenges
        self.challenges = [
            "CS2 b2b",
            "Rocket League b2b",
            "League of Legends 2 Wins",
            "1x Bloons (schwer)",
            "1x Fall Guys Win",
            "2x Brawlhalla Win",
            "DBD beide entkommen",
            "Plate Up 7 Tage",
            "2x Fifa Koop Win",
            "1x Folge Attack On Titan"
        ]
        
        self.check_vars = [tk.IntVar() for _ in range(10)]
        self.load_checkboxes()  # Zustände der Checkboxen laden
        self.create_checkboxes()
        self.ws = None
        self.websocket_thread = threading.Thread(target=self.start_websocket, daemon=True)
        self.websocket_thread.start()
        
        # Variablen für die Mausbewegung
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def create_checkboxes(self):
        # Moderne weiße Schrift auf dunklem Hintergrund für die Checkboxes
        for i, challenge in enumerate(self.challenges):
            chk = tk.Checkbutton(self.root, text=challenge, variable=self.check_vars[i],
                                 font=("Comic Sans MS", 12), bg="#1A1A1A", fg="#FFFFFF", selectcolor="#1A1A1A", 
                                 activebackground="#1A1A1A", activeforeground="#FFFFFF", command=self.update_check)
            chk.pack(anchor="w", padx=20)

    def update_check(self):
        # Senden der Checkbox-Änderung an den Server
        changes = [var.get() for var in self.check_vars]
        asyncio.run(self.send_updates(changes))
        self.save_checkboxes()  # Zustände der Checkboxen speichern

    async def send_updates(self, changes):
        if self.ws:
            await self.ws.send(str(changes))

    async def receive_updates(self):
        async for message in self.ws:
            changes = eval(message)
            # Aktualisiere die Checkboxen im GUI-Thread
            self.root.after(0, self.update_checkboxes, changes)

    def update_checkboxes(self, changes):
        for i, value in enumerate(changes):
            self.check_vars[i].set(value)

    def load_checkboxes(self):
        # Lade die Zustände der Checkboxen aus einer Datei
        if os.path.exists("checkbox_states.json"):
            with open("checkbox_states.json", "r") as f:
                states = json.load(f)
                for i, state in enumerate(states):
                    self.check_vars[i].set(state)

    def save_checkboxes(self):
        # Speichere die Zustände der Checkboxen in einer Datei
        states = [var.get() for var in self.check_vars]
        with open("checkbox_states.json", "w") as f:
            json.dump(states, f)

    async def connect(self):
        try:
            # Verbinde dich zum Server mit deiner Hamachi-IP
            self.ws = await websockets.connect("ws://25.14.227.10:8765")
            await self.receive_updates()
        except Exception as e:
            print(f"Verbindungsfehler: {e}")

    def start_websocket(self):
        # WebSocket in einem separaten asyncio-Event-Loop starten
        asyncio.run(self.connect())

    def start_drag(self, event):
        self.dragging = True
        # Speichere die Offset-Position
        self.offset_x = event.x
        self.offset_y = event.y

    def stop_drag(self, event):
        self.dragging = False

    def drag(self, event):
        if self.dragging:
            # Berechne die neue Position des Fensters
            x = self.root.winfo_x() + event.x - self.offset_x
            y = self.root.winfo_y() + event.y - self.offset_y
            self.root.geometry(f"+{x}+{y}")

# Initialisiere die GUI und das Overlay
root = tk.Tk()
overlay = Overlay(root)
root.mainloop()
