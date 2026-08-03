from sidecar.state_manager import StateJournal

journal = StateJournal()

# Simulate updating state for account 998877
account_id = 998877
print(f"[Test] Writing initial equity for account {account_id} ($50,000)...")
journal.update_account_state(account_id, current_equity=50000.0, locked=False)

# Simulate equity growth to new high-water mark
print(f"[Test] Updating equity to new peak ($51,500)...")
journal.update_account_state(account_id, current_equity=51500.0, locked=False)

# Retrieve state
state = journal.get_account_state(account_id)
print("[Test] Retrieved Mmap State Record:", state)
