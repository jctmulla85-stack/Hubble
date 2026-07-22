import json
import os

class StateManager:
    def __init__(self, filename="bot_state.json"):
        self.filename = filename
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {"positions": {}, "last_action": None}

    def save_all(self):
        with open(self.filename, 'w') as f:
            json.dump(self.state, f)

    def update_position(self, symbol, side, qty):
        if 'positions' not in self.state:
            self.state['positions'] = {}

        current = self.state['positions'].get(symbol, 0)
        if side == "buy":
            self.state['positions'][symbol] = current + qty
        elif side == "sell":
            self.state['positions'][symbol] = max(0, current - qty)
        self.save_all()
