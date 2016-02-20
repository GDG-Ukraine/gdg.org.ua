class InvalidFormDataError(Exception):
    def __init__(self, errors):
        self._errors = errors
