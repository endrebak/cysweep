from libcpp.vector cimport vector
from libc.stdlib cimport malloc

cdef extern from "stdlib.h":
    void free(void *)


cdef struct Interval:
    unsigned int start
    unsigned int end
    unsigned int index


# cdef void scan_cache(Interval query, vector[Interval] *db_cache, vector[Interval] *hits):

#     pass


cdef class SortedList:

    # the cache should be an array, not the intervals
    # cdef vector[Interval] intervals
    cdef Interval *intervals
    cdef int length


    def __cinit__(self, long [::1] starts, long [::1] ends, long [::1] indexes):

        cdef Interval *intervals = <Interval *> malloc(len(starts) * sizeof(Interval))
        length = len(starts)
        cdef int i = 0

        # need to check that starts are sorted and that ends are always after start
        # TODO: add this check
        for i in range(length):

            intervals.start = starts[i]
            intervals.end = ends[i]
            intervals.index = indexes[i]


    def find_overlaps(self, SortedList database): # self is the query

        cdef vector[Interval] db_cache
        cdef vector[int] to_remove
        cdef vector[int] database_hits
        cdef vector[int] query_hits

        cdef Interval query
        cdef Interval db
        cdef Interval _db

        db = database.intervals[0]

        for i in range(self.length):
            query = self.intervals[i]

            ##############
            # update cache
            for j in range(db_cache.size()):
                _db = db_cache[j]

                # Is a after (to the right of) b?
                # If so, never need to be looked at again.
                if not query.start >= _db.end:

                    # do the query and db overlap?
                    if (query.start < _db.end) and (_db.start < query.end):
                        database_hits.push_back(_db.index)
                        query_hits.push_back(query.index)
                else:
                    to_remove.push_back(j)

            if not to_remove.empty():
                for j in range(to_remove.size()):
                    # quick delete of object
                    # https://stackoverflow.com/questions/3487717/erasing-multiple-objects-from-a-stdvector
                    db_cache[to_remove[j]] = db_cache.back()
                    db_cache.pop_back()
            ##############

# def scan_cache(curr_qy, db_cache, hits):
#     """
#     Scan the cache of "in-play" intervals from the database
#     for overlaps.  If curr_qy is "after" (right of)
#     a cached intervals, the cached interval can be
#     removed from further consideration. We can trust
#     this because the files are position sorted.
#     """
#     if curr_qy is None:
#         return db_cache

#     temp_cache = []
#     for curr_db in db_cache:
#         if not after(curr_qy, curr_db):
#             temp_cache.append(curr_db)
#             if overlaps(curr_qy, curr_db) > 0:
#                 hits.append(curr_db)

#     return temp_cache









    def __dealloc__(self):

        free(self.intervals)

    def close(self):

        free(self.intervals)



def hi():
    cdef int i, x

    cdef Interval hi
    print(type(hi))

    hi.start = 1
    hi.end = 3
    hi.index = 5

    # vect.push_back(hi)
    # print(type(hi))

    # print(vect[0])
    # for i in range(10):
    #     vect.push_back(i)

    # for i in range(10):
    #     print(vect[i])

    # for x in vect:
    #     print(x)
