#!/usr/bin/env python3
"""Check which mail.thread models are missing form views."""
import re, os

base = '/root/workspace/kebun/odoo-data/addons/19.0'
mail_models = {}
form_models = set()

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.py') and '__pycache__' not in root:
            content = open(os.path.join(root, f)).read()
            if 'mail.thread' in content:
                m = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
                if m:
                    mail_models[m.group(1)] = os.path.join(root, f)

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.xml') and '__pycache__' not in root:
            content = open(os.path.join(root, f)).read()
            for view in re.findall(r'<record[^>]*>.*?</record>', content, re.DOTALL):
                if '<form' in view:
                    m = re.search(r'<field name="model">([^<]+)</field>', view)
                    if m:
                        form_models.add(m.group(1))

missing = [m for m in sorted(mail_models) if m not in form_models]
if missing:
    print(f'MISSING form views ({len(missing)}):')
    for m in missing:
        print(f'  {m}  ({mail_models[m]})')
else:
    print(f'All {len(mail_models)} mail.thread models have form views')

print(f'\nTotal mail.thread models: {len(mail_models)}')
print(f'Total models with form views: {len(form_models)}')
