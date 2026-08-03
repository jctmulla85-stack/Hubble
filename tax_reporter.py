import json
import hashlib
import os
from datetime import datetime

def test_tax_reporter():
    audit_file = "execution/audit_trail.jsonl"
    test_output = "alorle_tax_report_test.csv"
    
    print("--- STARTING TAX REPORTER TEST ---")
    
    # 1. Check if source audit trail exists
    if not os.path.exists(audit_file):
        print(f"⚠️ Warning: {audit_file} not found. Creating a mock audit entry for testing.")
        os.makedirs("execution", exist_ok=True)
        with open(audit_file, "w") as f:
            sample_entry = {"timestamp": str(datetime.utcnow()), "action": "FILL", "symbol": "AAPL", "qty": 10, "price": 150.0}
            f.write(json.dumps(sample_entry) + "\n")

    # 2. Read and parse log lines
    transactions = []
    sha256_hash = hashlib.sha256()
    
    with open(audit_file, "rb") as f:
        for line in f:
            sha256_hash.update(line)
            try:
                transactions.append(json.loads(line.decode().strip()))
            except json.JSONDecodeError:
                continue

    file_signature = sha256_hash.hexdigest()

    # 3. Generate test report
    with open(test_output, "w") as out:
        out.write("Timestamp,Action,Symbol,Quantity,Price\n")
        for tx in transactions:
            out.write(f"{tx.get('timestamp')},{tx.get('action')},{tx.get('symbol')},{tx.get('qty')},{tx.get('price')}\n")
            
    print(f"✅ Test Report Generated: {test_output}")
    print(f"🔒 Cryptographic Integrity Hash (SHA-256): {file_signature}")
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_tax_reporter()
