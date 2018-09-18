from libcpp.vector cimport vector
from libc.stdlib cimport malloc, free
cimport cython

import numpy as np


cdef struct Interval:
    unsigned int start
    unsigned int end
    unsigned int index


cdef class SortedList:

    # the cache should be an array, not the intervals
    # cdef vector[Interval] intervals
    cdef Interval *intervals
    cdef unsigned int length


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    def __cinit__(self, long [::1] starts, long [::1] ends, long [::1] indexes):

        self.intervals = <Interval *> malloc(len(starts) * sizeof(Interval))
        cdef unsigned int length = len(starts)
        cdef unsigned int i = 0
        self.length = length

        # need to check that starts are sorted and that ends are always after start
        # TODO: add this check
        for i in range(length):

            self.intervals[i].start = starts[i]
            self.intervals[i].end = ends[i]
            self.intervals[i].index = indexes[i]


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    def find_overlaps(self, SortedList database): # self is the query

        cdef vector[Interval] db_cache
        cdef vector[unsigned int] to_remove

        cdef unsigned int arr_length = self.length

        db_hits_arr = np.zeros(self.length, dtype=np.long)
        query_hits_arr = np.zeros(self.length, dtype=np.long)

        cdef long [::1] db_hits
        cdef long [::1] query_hits

        db_hits = db_hits_arr
        query_hits = query_hits_arr

        cdef Interval query
        cdef Interval db
        cdef Interval _db
        cdef unsigned int nfound = 0
        cdef unsigned int db_pos = 0
        cdef unsigned int db_cache_pos = 0
        cdef unsigned int to_remove_pos = 0

        db = database.intervals[0]

        # iterate over queries
        for i in range(self.length):
            query = self.intervals[i]

            ##################
            # scan the cache #
            ##################

            for db_cache_pos in range(int(db_cache.size())):
                _db = db_cache[db_cache_pos]

                if not query.start >= _db.end:

                    # do the query and db overlap?
                    if (query.start < _db.end) and (_db.start < query.end):
                        # need more space for hits
                        if nfound == arr_length:
                            arr_length = arr_length * 2
                            db_hits_arr = np.resize(db_hits_arr, arr_length)
                            query_hits_arr = np.resize(query_hits_arr, arr_length)
                            db_hits = db_hits_arr
                            query_hits = query_hits_arr

                        db_hits[nfound] = _db.index
                        query_hits[nfound] = query.index
                        nfound += 1
                # Is query after (to the right of) db_entry?
                # If so, never need to be looked at again.
                else:
                    to_remove.push_back(db_cache_pos)

            if not to_remove.empty():
                # if remove from back?
                for to_remove_pos in range(0, int(to_remove.size()), -1):
                    # quick delete of object, must start in back not to disturb delete positions
                    # https://stackoverflow.com/questions/3487717/erasing-multiple-objects-from-a-stdvector
                    db_cache[to_remove[to_remove_pos]] = db_cache.back()
                    db_cache.pop_back()
                to_remove.clear()

            # Keep advancing the database until we'e:
            # 1. reached EOF # 2. Reached an interval that is AFTER  the query (start > query's end)
            # We add each feature to the cache, and track those that overlap
            while db_pos < database.length and not database.intervals[db_pos].start >= query.end:
                _db = database.intervals[db_pos]
                if (query.start < _db.end) and (_db.start < query.end):
                    # need more space for hits
                    if nfound == arr_length:
                        arr_length = arr_length * 2
                        db_hits_arr = np.resize(db_hits_arr, arr_length)
                        query_hits_arr = np.resize(query_hits_arr, arr_length)
                        db_hits = db_hits_arr
                        query_hits = query_hits_arr

                    db_hits[nfound] = _db.index
                    query_hits[nfound] = query.index
                    nfound += 1

                db_cache.push_back(_db)
                db_pos += 1

        return query_hits_arr[:nfound], db_hits_arr[:nfound]


    def find_overlaps_interval(self, start, end):

        # slow, but likely good enough
        # not to be used in a loop or anything XD

        pass


    def __dealloc__(self):

        if self.intervals:
            free(self.intervals)
