"""Structural checks for a Live set (.als): unique pointee Ids below NextPointeeId,
unique track Ids, no dangling PointeeId references, unique LomId definitions, and every
Max mapping (MxDIdRef) resolving to a LomId defined in the set.

Usage: python scripts/als_validate.py set.als
"""
import gzip, sys, collections, xml.etree.ElementTree as ET
r=ET.parse(gzip.open(sys.argv[1])).getroot()
npid=int(r.find('LiveSet/NextPointeeId').get('Value'))
ids=collections.Counter(e.get('Id') for e in r.iter() if (e.tag=='Pointee' or e.tag.endswith('Target')) and e.get('Id') is not None)
dup=[k for k,v in ids.items() if v>1]; over=[k for k in ids if int(k)>=npid]
tids=collections.Counter(t.get('Id') for t in r.find('LiveSet/Tracks'))
pids={e.get('Value') for e in r.iter('PointeeId')}
dangling=[p for p in pids if p not in ids and p!='0']
# LomId definitions: elements whose direct child LomId is not in MxDIdRef
par={c:p for p in r.iter() for c in p}
defs=collections.Counter(e.get('Value') for e in r.iter('LomId') if e.get('Value')!='0' and par[e].tag!='MxDIdRef')
lomdup=[k for k,v in defs.items() if v>1]
refs={e.find('LomId').get('Value') for e in r.iter('MxDIdRef')}-{'0'}
unres=[x for x in refs if x not in defs]
print(f"pointees={len(ids)} dup={dup[:5]} >=Next={over[:5]} trackIdDup={[k for k,v in tids.items() if v>1]} danglingPointeeRefs={len(dangling)} lomDefDup={lomdup[:5]} unresolvedMxDRefs={unres}")
