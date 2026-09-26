import json, sys

d = json.load(open('onbob-output/atlas_data.json', encoding='utf-8'))

# Validate top-level meta
assert d['generated_by'] == 'IBM Bob 2.0', 'Wrong generator'
assert d['repo_name'] == 'target-repo', 'Wrong repo name'
assert d['stack'] == 'FastAPI', 'Wrong stack'
assert len(d['pillars']) == 6, f'Expected 6 pillars, got {len(d["pillars"])}'
assert len(d['edges']) == 9, f'Expected 9 edges, got {len(d["edges"])}'
assert len(d['features']) == 6, f'Expected 6 features, got {len(d["features"])}'
assert len(d['features_menu']) == 6, f'Expected 6 menu items, got {len(d["features_menu"])}'
assert len(d['health']) == 6, f'Expected 6 health entries'
assert len(d['blast_data']) == 6, f'Expected 6 blast entries'
assert len(d['quest']['phases']) == 3, 'Expected 3 quest phases'

# Validate pillar IDs match across sections
pids = {p['id'] for p in d['pillars']}
health_pids = set(d['health'].keys())
blast_pids = set(d['blast_data'].keys())
assert pids == health_pids, f'Health mismatch: {pids} vs {health_pids}'
assert pids == blast_pids, f'Blast mismatch: {pids} vs {blast_pids}'

# Validate each pillar has required fields
required_fields = ['id','name','icon','mission','team','color','rgb','files','depends_on','dependents']
for p in d['pillars']:
    missing = [k for k in required_fields if k not in p]
    assert not missing, f'Pillar {p["id"]} missing fields: {missing}'

# Validate edge references valid pillar ids
for e in d['edges']:
    src = e['source']
    tgt = e['target']
    assert src in pids, f'Edge source {src} not in pillars {pids}'
    assert tgt in pids, f'Edge target {tgt} not in pillars {pids}'

print('All validations passed!')
print(f'  Pillars    : {len(d["pillars"])} -- {sorted(pids)}')
print(f'  Edges      : {len(d["edges"])}')
print(f'  Traces     : {len(d["features"])}')
print(f'  Quest phases: {len(d["quest"]["phases"])}')
print(f'  Health keys : {sorted(health_pids)}')
print(f'  Blast keys  : {sorted(blast_pids)}')
