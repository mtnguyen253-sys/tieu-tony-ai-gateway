import re
with open("TECH_DEBT.md", "r") as f:
    content = f.read()
# Revert everything to Open first
content = content.replace("Status**: Resolved (Sprint 15)", "Status**: Open")
# Then only resolve TD-006
content = re.sub(
    r"(## TD-006.*?)(-\s*\*\*Status\*\*: )\w+(.*?)",
    r"\1\2Resolved (Sprint 15)\3",
    content, flags=re.DOTALL
)
with open("TECH_DEBT.md", "w") as f:
    f.write(content)
