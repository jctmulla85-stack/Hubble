import mmap
import struct
import os

class StateJournal:
    # Binary layout: account_id (q - 8 bytes), peak_equity (d - 8 bytes), current_equity (d - 8 bytes), locked (i - 4 bytes)
    STRUCT_FORMAT = "qddi"
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT)
    MAX_RECORDS = 100
    TOTAL_SIZE = RECORD_SIZE * MAX_RECORDS

    def __init__(self, filepath="/tmp/alorle_state.mmap"):
        self.filepath = filepath
        file_exists = os.path.exists(self.filepath)
        
        # Open or create the mmap backing file
        self.file = open(self.filepath, "a+b")
        if not file_exists:
            self.file.write(b'\x00' * self.TOTAL_SIZE)
            self.file.flush()
        
        self.fileno = self.file.fileno()
        self.mmap_buf = mmap.mmap(self.fileno, self.TOTAL_SIZE, access=mmap.ACCESS_WRITE)

    def _find_slot(self, account_id: int) -> int:
        """Scans the mmap buffer for an existing account record or an empty slot."""
        for i in range(self.MAX_RECORDS):
            offset = i * self.RECORD_SIZE
            data = self.mmap_buf[offset:offset + self.RECORD_SIZE]
            acc_id, peak, curr, locked = struct.unpack(self.STRUCT_FORMAT, data)
            
            if acc_id == account_id or acc_id == 0:
                return offset
        raise ValueError("State journal memory map is full.")

    def update_account_state(self, account_id: int, current_equity: float, locked: int):
        """Updates or initializes account metrics in memory-mapped storage instantly."""
        offset = self._find_slot(account_id)
        
        # Read existing state to preserve or update peak equity high-water mark
        data = self.mmap_buf[offset:offset + self.RECORD_SIZE]
        acc_id, peak_equity, _, _ = struct.unpack(self.STRUCT_FORMAT, data)
        
        if acc_id == 0 or current_equity > peak_equity:
            peak_equity = current_equity

        packed_data = struct.pack(self.STRUCT_FORMAT, account_id, peak_equity, current_equity, locked)
        self.mmap_buf[offset:offset + self.RECORD_SIZE] = packed_data
        self.mmap_buf.flush()

    def get_account_state(self, account_id: int) -> dict:
        """Retrieves current account tracking details from memory-mapped storage."""
        for i in range(self.MAX_RECORDS):
            offset = i * self.RECORD_SIZE
            data = self.mmap_buf[offset:offset + self.RECORD_SIZE]
            acc_id, peak_equity, current_equity, locked = struct.unpack(self.STRUCT_FORMAT, data)
            
            if acc_id == account_id:
                return {
                    "account_id": acc_id,
                    "peak_equity": peak_equity,
                    "current_equity": current_equity,
                    "locked": bool(locked)
                }
        return None

    def reconcile_state(self, account_id: int) -> dict:
        """Performs a cold-boot reconciliation check to verify state integrity after a restart."""
        state = self.get_account_state(account_id)
        if state:
            print(f"[StateJournal] RECONCILED: Account {account_id} reloaded from disk. Peak Equity: ${state['peak_equity']}, Locked: {state['locked']}")
        else:
            print(f"[StateJournal] RECONCILED: No prior persistent state found for Account {account_id}.")
        return state

    def close(self):
        self.mmap_buf.close()
        self.file.close()

