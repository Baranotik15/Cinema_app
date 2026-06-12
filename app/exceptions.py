class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id: int):
        self.message = f"{entity} with id {entity_id} not found"
        super().__init__(self.message)


class AlreadyExistsError(Exception):
    def __init__(self, entity: str, field: str, value: str):
        self.message = f"{entity} with {field}='{value}' already exists"
        super().__init__(self.message)


class DatabaseError(Exception):
    def __init__(self, message: str = "Database error occurred"):
        self.message = message
        super().__init__(self.message)
