path = "execution/worker.py"
f = open(path, "r")
lines = f.readlines()
f.close()
new_lines = []
for i, line in enumerate(lines):
    if "def __init__" in line:
        new_lines.append(line)
        if i + 1 < len(lines):
   