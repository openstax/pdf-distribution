from request import Request

class Event:
    def __init__(self, data):
        self.data = data;

    def request(self):
        return Request(self.data['Records'][0]['cf']['request'])
