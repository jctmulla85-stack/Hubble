import sys

class OrderFlowGuard:
    def __init__(self, imbalance_threshold=0.75):
        self.threshold = imbalance_threshold

    def evaluate_imbalance(self, bid_volume, ask_volume):
        """
        Evaluates book pressure. Returns True if flow is clean,
        or triggers a defensive halt/skip if toxic imbalance is detected.
        """
        total_volume = bid_volume + ask_volume
        if total_volume <= 0:
            return True  # No volume data, allow pass or handle gracefully

        bid_ratio = bid_volume / total_volume
        ask_ratio = ask_volume / total_volume

        # If either side exceeds our toxicity threshold, flag excessive imbalance
        if bid_ratio > self.threshold or ask_ratio > self.threshold:
            return False  # Toxic flow detected, step aside

        return True
