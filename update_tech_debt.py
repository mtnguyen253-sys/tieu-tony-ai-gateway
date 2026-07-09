import re
with open("TECH_DEBT.md", "r") as f:
    content = f.read()

content = re.sub(
    r"(## TD-001.*?)(-\s*\*\*Status\*\*: )\w+(.*?)",
    r"\1\2Resolved (Sprint 16)\3",
    content, flags=re.DOTALL
)

with open("TECH_DEBT.md", "w") as f:
    f.write(content)
