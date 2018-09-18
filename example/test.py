from chromsweep.src.chromsweep import SortedList

import pandas as pd
import numpy as np

db = pd.read_table("chr1_knowngene.bed.gz", header=None, usecols=[0, 1, 2], names="Chromosome Start End".split(), index_col=False)
qs = pd.read_table("chr1_rmsk.bed.gz", header=None, usecols=[0, 1, 2], names="Chromosome Start End".split(), index_col=False)

db_sl = SortedList(db.Start.values, db.End.values, db.index.values)
qs_sl = SortedList(qs.Start.values, qs.End.values, qs.index.values)

q_hits, db_hits = db_sl.find_overlaps(qs_sl)
print(len(q_hits), len(db_hits))
