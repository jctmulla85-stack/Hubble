import json
import re

input_file = "/home/Mulla85/logs/trading_audit.log"
output_file = "/home/Mulla85/logs/trading_audit_parsed.jsonl"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[INFO\] (.*)", line)
        if match:
            entry = {
                "timestamp": match.group(1),
                "message": match.group(2)
            }
            outfile.write(json.dumps(entry) + "\n")
