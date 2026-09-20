"""Fix conftest imports in test files to use relative imports."""
import os
import re

base = r'C:\Users\Anubhav Prakash\Music\Infosys\Customer-Insights-Platform\authentication\tests'
files = [f for f in os.listdir(base) if f.startswith('test_') and f.endswith('.py')]

for fname in files:
    path = os.path.join(base, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Replace 'from conftest import' with 'from authentication.tests.conftest import'
    content = content.replace('from conftest import', 'from authentication.tests.conftest import')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {fname}")
