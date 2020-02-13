
class SessionStorage:
    def __init__(self):
        self.data = {'user': '', 'meta': ''}

    def __str__(self):
        return str(self.data)
