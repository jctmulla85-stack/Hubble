path = "execution/worker.py"
with open(path, "r") as f:
    lines = f.readlines()
new_lines = []
skip = False
for i, line in enumerate(lines):
    if skip:
        skip = False
        continue
    new_lines.append(line)
    if "try:" in line and i + 1 < len(lines):
        nxt = lines[i+1]
        if not nxt.startswith("            "):
            new_lines.append("            " + nxt.lstrip())
            skip = True
with open(path, "w") as f:
    f.writelines(new_lines)
