

class DIContainer:
    def __init__(self) -> None:
        self.container = {}

    def get_instance(self, object_name: str):
        if object_name not in self.container:
            raise Exception(f"Object {object_name} not found")
        return self.container[object_name]

    def add_singleton(self, object_type, **kwargs) -> None:
        if object_type.__name__ not in self.container:
            self.container[object_type.__name__] = object_type(**kwargs)
        else:
            raise Exception(f"Object {object_type.__name__} already exists")
