from enum import Enum

class BiologicalGenre(str, Enum):
    @classmethod
    def create(cls, genres):
        enum_dict = {genre: genre for genre in genres}
        return Enum('BiologicalGenre', enum_dict, type=str)
    
class DocumentTypes(str, Enum):
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('DocumentTypes', enum_dict, type=str)
    
class Specialities(str, Enum):
    @classmethod
    def create(cls, documents):
        enum_dict = {typ: typ for typ in documents}
        return Enum('Specialities', enum_dict, type=str)