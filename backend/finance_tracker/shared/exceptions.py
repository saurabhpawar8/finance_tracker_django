from django.contrib.messages.context_processors import messages


class AlreadyExists(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ResourceNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
