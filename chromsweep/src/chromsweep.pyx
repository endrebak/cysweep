from libcpp.vector cimport vector

# cimport chromsweep.src.ccs as cs
cdef struct Interval:
    unsigned int start
    unsigned int end
    unsigned int index


def hi():
    cdef vector[Interval] vect
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
