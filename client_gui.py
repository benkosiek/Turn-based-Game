# `client_gui.py`


import socket
import threading
import json
import queue
import tkinter as tk
from tkinter import ttk, messagebox

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 50007

class NetClient:
    def __init__(self, host, port, incoming_q):
        self.host = host
        self.port = port
        self.incoming_q = incoming_q
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        self.alive = False

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.alive = True
        threading.Thread(target=self._reader, daemon=True).start()

    def send(self, obj: dict):
        data = (json.dumps(obj) + "\n").encode("utf-8")
        with self.lock:
            self.sock.sendall(data)

    def _reader(self):
        buf = b""
        while self.alive:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        msg = json.loads(line.decode("utf-8"))
                        self.incoming_q.put(msg)
                    except Exception:
                        pass
            except Exception:
                break
        self.incoming_q.put({"type": "error", "message": "Disconnected from server."})
        self.alive = False

    def close(self):
        self.alive = False
        try:
            self.sock.close()
        except Exception:
            pass

class BattleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Battle Game - Tkinter Client")
        self.geometry("840x600")

        self.incoming_q = queue.Queue()
        self.client = NetClient(SERVER_HOST, SERVER_PORT, self.incoming_q)

        # UI state
        self.player_id = None
        self.available_classes = []
        self.targets_enemy = []
        self.targets_ally = []
        self.is_my_turn = False

        # Layout
        self._build_widgets()

        # Connect
        try:
            self.client.connect()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.destroy()
            return

        # Start polling
        self.after(50, self._poll_messages)

    # ----------------------
    # UI construction
    # ----------------------
    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top bar
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        top.columnconfigure(2, weight=1)

        ttk.Label(top, text="Server:").grid(row=0, column=0)
        ttk.Label(top, text=f"{SERVER_HOST}:{SERVER_PORT}").grid(row=0, column=1)

        self.status_lbl = ttk.Label(top, text="Connecting...")
        self.status_lbl.grid(row=0, column=2, sticky="e")

        # Main panels
        main = ttk.Frame(self)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        # Team panels
        self.team1_box = tk.Text(main, height=12)
        self.team2_box = tk.Text(main, height=12)
        self.team1_box.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.team2_box.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.team1_box.configure(state="disabled")
        self.team2_box.configure(state="disabled")

        # Log panel
        self.log_box = tk.Text(main)
        self.log_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.log_box.configure(state="disabled")

        # Action panel
        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, sticky="ew", padx=10, pady=8)
        actions.columnconfigure(6, weight=1)

        ttk.Label(actions, text="Action:").grid(row=0, column=0, padx=4)
        self.action_var = tk.StringVar(value="attack")
        self.action_cb = ttk.Combobox(actions, textvariable=self.action_var, values=["attack","defend","special"], state="readonly")
        self.action_cb.grid(row=0, column=1, padx=4)
        self.action_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_target_visibility())

        ttk.Label(actions, text="Target (enemy):").grid(row=0, column=2, padx=4)
        self.target_enemy_var = tk.StringVar()
        self.target_enemy_cb = ttk.Combobox(actions, textvariable=self.target_enemy_var, values=[])
        self.target_enemy_cb.grid(row=0, column=3, padx=4)

        ttk.Label(actions, text="Target (ally):").grid(row=0, column=4, padx=4)
        self.target_ally_var = tk.StringVar()
        self.target_ally_cb = ttk.Combobox(actions, textvariable=self.target_ally_var, values=[])
        self.target_ally_cb.grid(row=0, column=5, padx=4)

        self.submit_btn = ttk.Button(actions, text="Submit", command=self._submit_action, state="disabled")
        self.submit_btn.grid(row=0, column=6, padx=4, sticky="e")

        # Character selection frame (overlays early on)
        self.char_frame = ttk.LabelFrame(self, text="Choose Your Character")
        self.char_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.char_buttons = []

    # ----------------------
    # Event handling
    # ----------------------
    def _poll_messages(self):
        while True:
            try:
                msg = self.incoming_q.get_nowait()
            except queue.Empty:
                break
            self._handle_message(msg)
        self.after(50, self._poll_messages)

    def _handle_message(self, msg: dict):
        mtype = msg.get("type")
        if mtype == "welcome":
            self.player_id = msg.get("player_id")
            self.status_lbl.config(text=f"Connected. You are Player {self.player_id}")
        elif mtype == "choose_character":
            self.available_classes = msg.get("available", [])
            self._show_character_choices()
        elif mtype == "waiting":
            self._append_log(msg.get("message", "Waiting..."))
        elif mtype == "game_state":
            # Hide the selector when the server starts broadcasting match state
            if self.char_frame.winfo_ismapped():
                self.char_frame.place_forget()
            self._render_state(msg.get("state", {}))
        elif mtype == "your_turn":
            self.is_my_turn = True
            cd = msg.get("cooldown", 0)

            # Determine available actions based on cooldown
            acts = ["attack", "defend"] if cd > 0 else ["attack", "defend", "special"]

            t = msg.get("targets", {})
            self.targets_enemy = t.get("enemy", [])
            self.targets_ally = t.get("ally", [])

            # Update dropdowns
            self.action_cb["values"] = acts
            if cd > 0 and self.action_var.get() == "special":
                self.action_var.set("attack")
            self.target_enemy_cb["values"] = self.targets_enemy
            self.target_ally_cb["values"] = self.targets_ally
            self._refresh_target_visibility()

            # Enable submit
            self.submit_btn.config(state="normal")

            # Log and status label
            actor = msg.get("actor", "Your")
            self._append_log(f"It's your turn: {actor}")
            if cd > 0:
                self._append_log(f"Your special move is on cooldown for {cd} more turn(s).")
            self.status_lbl.config(text="Your turn!")

        elif mtype == "action_result":
            self._append_log(msg.get("log", ""))
        elif mtype == "game_over":
            winner = msg.get("winner")
            self._append_log(f"Game Over! Winner: {winner}")
            self.submit_btn.config(state="disabled")
            messagebox.showinfo("Game Over", f"Winner: {winner}")
        elif mtype == "error":
            self._append_log("Error: " + msg.get("message", ""))
            # If character was taken, let the user pick again
            if not self.char_frame.winfo_ismapped():
                self.char_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # ignore unknown
            pass

    def _show_character_choices(self):
        # Clear previous
        for btn in self.char_buttons:
            btn.destroy()
        self.char_buttons = []

        # Build buttons
        for i, name in enumerate(self.available_classes):
            b = ttk.Button(self.char_frame, text=name, command=lambda n=name: self._pick_character(n))
            b.grid(row=i//3, column=i%3, padx=6, pady=6)
            self.char_buttons.append(b)

    def _pick_character(self, name):
        try:
            self.client.send({"type": "pick_character", "choice": name})
        except Exception as e:
            messagebox.showerror("Network", str(e))
            return
        self._append_log(f"You picked {name}. Waiting for opponent...")

    def _render_state(self, state: dict):
        teams = state.get("teams", {})
        # Left: Team 1, Right: Team 2
        self._set_text(self.team1_box, self._format_team(teams.get("Team 1", []), title="Team 1"))
        self._set_text(self.team2_box, self._format_team(teams.get("Team 2", []), title="Team 2"))

    def _format_team(self, members, title="Team"):
        lines = [title, "=" * len(title), ""]
        for m in members:
            if not m:
                continue
            status = ", ".join(m.get("status", [])) or "None"
            lines.append(f"{m['name']:12s} | HP: {m['hp']:>3} | DEF: {m['defense']:>2} | CD: {m['cooldown']} | Status: {status}")
        return "\n".join(lines)

    def _set_text(self, widget: tk.Text, txt: str):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, txt)
        widget.configure(state="disabled")

    def _append_log(self, line: str):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, line + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def _refresh_target_visibility(self):
        act = self.action_var.get()
        # enable/disable target boxes. We'll show both; server will validate which one matters.
        if act == "defend":
            self.target_enemy_cb.set("")
            self.target_ally_cb.set("")
            self.target_enemy_cb.configure(state="disabled")
            self.target_ally_cb.configure(state="disabled")
        else:
            self.target_enemy_cb.configure(state="readonly")
            self.target_ally_cb.configure(state="readonly")

    def _submit_action(self):
        if not self.is_my_turn:
            return
        act = self.action_var.get()
        target_index = None
        # Prefer enemy target if selected, else ally
        if self.target_enemy_var.get() in self.targets_enemy:
            target_index = self.targets_enemy.index(self.target_enemy_var.get())
        elif self.target_ally_var.get() in self.targets_ally:
            target_index = self.targets_ally.index(self.target_ally_var.get())

        try:
            self.client.send({
                "type": "action",
                "action": act,
                "target_index": target_index
            })
        except Exception as e:
            messagebox.showerror("Network", str(e))
            return

        self.submit_btn.config(state="disabled")
        self.is_my_turn = False
        self.status_lbl.config(text="Waiting for opponent...")

    def destroy(self):
        try:
            self.client.close()
        except Exception:
            pass
        super().destroy()

if __name__ == "__main__":
    app = BattleApp()
    app.mainloop()
