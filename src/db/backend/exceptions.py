class DatabaseError(Exception):
    pass

class TableNotFoundError(DatabaseError):
    pass

class RecordNotFoundError(DatabaseError):
    pass

class ValidationError(DatabaseError):
    pass