import os
log_path = "worker.log"
if os.path.exists(log_path):
    with open(log_path, "r") as f:
        print(f.read())
else:
    print("worker.log does not exist.")
