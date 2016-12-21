cdef extern from "KrovetzStemmer.hpp" namespace "stem":
    cdef cppclass KrovetzStemmer:
        KrovetzStemmer()
        char* kstem_stemmer(char*)
        int kstem_stem_tobuffer(char*, char*)
