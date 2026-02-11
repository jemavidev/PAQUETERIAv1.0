#!/usr/bin/env python3
"""
Script para verificar que solo existe 1 head en las migraciones de Alembic
"""
import re
import os

migrations = {}
versions_dir = "CODE/alembic/versions"

# Leer todas las migraciones
for filename in os.listdir(versions_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(versions_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Extraer revision
        rev_match = re.search(r"^revision = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        if not rev_match:
            continue
        revision = rev_match.group(1)
        
        # Extraer down_revision (manejar multi-línea)
        down_match = re.search(r"^down_revision = (.+?)(?=^branch_labels)", content, re.MULTILINE | re.DOTALL)
        if down_match:
            down_str = down_match.group(1)
            if 'None' in down_str:
                down_revisions = []
            else:
                down_revisions = re.findall(r"['\"]([^'\"]+)['\"]", down_str)
        else:
            down_revisions = []
        
        migrations[revision] = {
            'file': filename,
            'down_revision': down_revisions
        }

# Encontrar heads
all_revisions = set(migrations.keys())
referenced_revisions = set()
for rev, data in migrations.items():
    referenced_revisions.update(data['down_revision'])

heads = all_revisions - referenced_revisions

print(f"✅ Total de migraciones: {len(migrations)}")
print(f"{'✅' if len(heads) == 1 else '❌'} Total de heads: {len(heads)}")

if len(heads) == 1:
    print("\n✅ CORRECTO: Solo existe 1 head")
    for head in heads:
        print(f"   Head: {head}")
        print(f"   Archivo: {migrations[head]['file']}")
else:
    print("\n❌ ERROR: Existen múltiples heads")
    for head in sorted(heads):
        print(f"   - {head} ({migrations[head]['file']})")

exit(0 if len(heads) == 1 else 1)
