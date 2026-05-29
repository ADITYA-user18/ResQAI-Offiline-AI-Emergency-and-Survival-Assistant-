"""
check_data.py — ResQAI Data Integrity Diagnostic
=================================================
Run from: ResQAI/backend/
    python check_data.py
"""

import json
import sys
from pathlib import Path
from collections import Counter

ROOT    = Path(__file__).resolve().parent.parent
META    = ROOT / "knowledge" / "embeddings" / "metadata.json"
FIDX    = ROOT / "knowledge" / "embeddings" / "faiss.index"
FA_JSON = ROOT / "knowledge" / "processed" / "firstaid.json"
SV_JSON = ROOT / "knowledge" / "processed" / "survival.json"
LG_JSON = ROOT / "knowledge" / "processed" / "legal.json"

SEP = "=" * 55

# ─────────────────────────────────────────────────────────────
# 1.  METADATA.JSON
# ─────────────────────────────────────────────────────────────
print(SEP)
print("  METADATA.JSON ANALYSIS")
print(SEP)

with open(META, encoding="utf-8") as f:
    metadata = json.load(f)

total_entries = len(metadata)
vector_ids    = [e["vector_id"] for e in metadata]
min_id        = min(vector_ids)
max_id        = max(vector_ids)

print(f"Total entries   : {total_entries}")
print(f"vector_id range : {min_id}  to  {max_id}")
print(f"Expected count  : {max_id - min_id + 1}")

# Check for gaps
expected_ids = set(range(min_id, max_id + 1))
actual_ids   = set(vector_ids)
missing_ids  = sorted(expected_ids - actual_ids)
if missing_ids:
    print(f"MISSING IDs     : {missing_ids}")
else:
    print("Missing IDs     : None - sequence is continuous")

# Check for duplicates
seen = {}
dups = []
for vid in vector_ids:
    seen[vid] = seen.get(vid, 0) + 1
dups = [vid for vid, cnt in seen.items() if cnt > 1]
if dups:
    print(f"DUPLICATE IDs   : {dups}")
else:
    print("Duplicate IDs   : None")

# Category breakdown
cats = Counter(e.get("category", "unknown") for e in metadata)
print(f"Categories      : {dict(cats)}")

# Priority breakdown
pris = Counter(e.get("priority", "unknown") for e in metadata)
print(f"Priorities      : {dict(pris)}")

# ─────────────────────────────────────────────────────────────
# 2.  FAISS INDEX
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print("  FAISS INDEX ANALYSIS")
print(SEP)

try:
    import faiss
    index = faiss.read_index(str(FIDX))
    print(f"Vector count (ntotal) : {index.ntotal}")
    print(f"Vector dimension (d)  : {index.d}")
    print(f"File size             : {FIDX.stat().st_bytes if hasattr(FIDX.stat(),'st_bytes') else FIDX.stat().st_size} bytes")
except ImportError:
    print("faiss-cpu not installed -- reading file size only")
    print(f"File size : {FIDX.stat().st_size} bytes")
    index = None

# ─────────────────────────────────────────────────────────────
# 3.  ALIGNMENT CHECK
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print("  ALIGNMENT CHECK")
print(SEP)

if index is not None:
    faiss_count = index.ntotal
    if faiss_count == total_entries:
        print(f"OK  FAISS vectors ({faiss_count}) == metadata entries ({total_entries})")
    else:
        print(f"MISMATCH  FAISS: {faiss_count}  vs  Metadata: {total_entries}")
        diff = faiss_count - total_entries
        if diff > 0:
            print(f"  -> FAISS has {diff} MORE vectors than metadata entries!")
            print("     Those extra vectors have NO metadata and cannot be retrieved.")
        else:
            print(f"  -> Metadata has {abs(diff)} MORE entries than FAISS vectors!")
            print("     Those metadata entries point to non-existent vectors.")

    if faiss_count == max_id + 1:
        print(f"OK  FAISS ntotal ({faiss_count}) == max_vector_id+1 ({max_id + 1})")
    else:
        print(f"NOTE  FAISS ntotal={faiss_count}, max_vector_id+1={max_id + 1}")
else:
    print("Skipped (faiss-cpu not installed)")

# ─────────────────────────────────────────────────────────────
# 4.  PROCESSED JSON COVERAGE
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print("  PROCESSED JSON COVERAGE")
print(SEP)

knowledge_map = {}
for label, path in [("firstaid", FA_JSON), ("survival", SV_JSON), ("legal", LG_JSON)]:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for e in entries:
            if "id" in e:
                knowledge_map[e["id"]] = e
        print(f"{label:10s} : {len(entries)} chunks  ({path.name})")
    else:
        print(f"{label:10s} : FILE NOT FOUND ({path})")

print(f"Total knowledge chunks : {len(knowledge_map)}")

# Check every metadata ID has a matching text entry
missing_text = []
for entry in metadata:
    cid = entry.get("id")
    if cid and cid not in knowledge_map:
        missing_text.append(cid)

if missing_text:
    print(f"MISSING in processed JSONs ({len(missing_text)} IDs):")
    for mid in missing_text[:20]:
        print(f"  - {mid}")
    if len(missing_text) > 20:
        print(f"  ... and {len(missing_text)-20} more")
else:
    print("All metadata IDs found in processed JSONs -- perfect match")

# Check for orphan IDs in processed JSONs not in metadata
meta_ids = set(e.get("id") for e in metadata)
orphan   = [cid for cid in knowledge_map if cid not in meta_ids]
if orphan:
    print(f"ORPHAN chunks in JSONs not in metadata ({len(orphan)}):")
    for oid in orphan[:10]:
        print(f"  - {oid}")
else:
    print("No orphan chunks -- all processed JSON entries are indexed in metadata")

print()
print(SEP)
print("  SUMMARY")
print(SEP)
print(f"metadata.json  : {total_entries} entries  (vector_id {min_id} to {max_id})")
if index:
    match = "MATCH" if index.ntotal == total_entries else "MISMATCH"
    print(f"faiss.index    : {index.ntotal} vectors  ({match})")
print(f"processed JSONs: {len(knowledge_map)} chunks")
txt_match = "MATCH" if not missing_text and not orphan else "MISMATCH"
print(f"ID coverage    : {txt_match}")
print(SEP)
