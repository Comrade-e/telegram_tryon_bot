class UserChoicesDict:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dct=None):
        if dct is None:
            dct = dict()
        if not hasattr(self, "_initialized"):
            self.DICT = dct
            self._initialized = True
