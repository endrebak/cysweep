#!/usr/bin/env python
import sys

from collections import namedtuple

def after(a, b):
    """
    Is a after (to the right of) b?
    If so, never need to be looked at again.
    """
    return a.start >= b.end

def report_hits(curr_qy, hits):
    """
    Report the number of overlaps b/w query and database
    """
    print(str(curr_qy) + "\t" + str(len(hits)))


def overlaps(a, b):
    """
    Return the amount of overlap, in bp
    between a and b.
    If >0, the number of bp of overlap
    If 0,  they are book-ended.
    If <0, the distance in bp between them
    """
    if b is not None:
        return min(a.end, b.end) - max(a.start, b.start)
    else:
        return -1


def scan_cache(curr_qy, db_cache, hits):
    """
    Scan the cache of "in-play" intervals from the database
    for overlaps.  If curr_qy is "after" (right of)
    a cached intervals, the cached interval can be
    removed from further consideration. We can trust
    this because the files are position sorted.
    """
    if curr_qy is None:
        return db_cache

    temp_cache = []
    for curr_db in db_cache:
        if not after(curr_qy, curr_db):
            temp_cache.append(curr_db)
            if overlaps(curr_qy, curr_db) > 0:
                hits.append(curr_db)

    return temp_cache


def get_next(ivls):
    """
    Get the next interval in a file (ivls).
    Return None if at EOF
    """
    try:
        return next(ivls)
    except StopIteration:
        return None



def sweep(query, database):
    """
    Sweep through query and DB (interval files) in one pass
    and detect overlaps on the fly.

    In BEDTools parlance, query == A, DB == B
    """
    hits  = []
    db_cache = []

    curr_db = get_next(database)

    for curr_qy in query:

        db_cache = scan_cache(curr_qy, db_cache, hits)

        while (curr_db is not None and not after(curr_db, curr_qy)):
            if (overlaps(curr_qy, curr_db) > 0):
                hits.append(curr_db)
            db_cache.append(curr_db)
            curr_db = get_next(database)

        report_hits(curr_qy, hits)
        hits = []


def file_to_intervals(f):

    if f.endswith(".gz"):
        raise Exception(".gz files not supported!")

    for line in open(f):
        start, end = line.split()[1:3]
        start, end = int(start), int(end)
        yield Interval(start, end)

if __name__ == "__main__":

    # no sort, usually

    # worst case, one sort, one linear pass

    if len(sys.argv) < 3:
        print("Usage:")
        print("chrom_sweep.py [query] [database]")
        sys.exit()

    query_file = sys.argv[1]
    database_file = sys.argv[2]

    Interval = namedtuple("Interval", ["start", "end"])

    query = file_to_intervals(query_file)
    database = file_to_intervals(database_file)

    sweep(query, database)
