import re

with open("src/App.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Find all JSX components <Name
components = set(re.findall(r'<([A-Z][a-zA-Z0-9_]*)', code))
print("JSX Components used in App.jsx:")
print(components)
