from enum import Enum

class BiologicalGenre(str, Enum):
    '''Biological genres for patients and doctors
    Takes a list of genres and creates an Enum
    '''
    @classmethod
    def create(cls, genres):
        enum_dict = {genre: genre for genre in genres}
        return Enum('BiologicalGenre', enum_dict, type=str)
    
class DocumentTypes(str, Enum):
    '''Document types for patients and doctors
    Takes a list of document types and creates an Enum
    '''
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('DocumentTypes', enum_dict, type=str)
    
class Specialities(str, Enum):
    '''Medical specialities for doctors
    Takes a list of specialities and creates an Enum
    '''
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('Specialities', enum_dict, type=str)

class Hospitals(str, Enum):
    '''Hospitals for medical appointments
    Takes a list of hospitals and creates an Enum
    '''
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('Hospitals', enum_dict, type=str)

class Months(str, Enum):
    '''Months for medical appointments
    Takes a list of months and creates an Enum
    '''
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('Months', enum_dict, type=str)