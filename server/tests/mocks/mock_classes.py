class MockContext:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def dict(self):
        return {"context": "mock_context"}
