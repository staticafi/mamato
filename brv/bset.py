class BSet(object):
    def __init__(self, name, bid):
        self.name = name
        self.id = bid

    def __hash__(self):
        return self.id

    def __eq__(self, oth):
        return self.id == oth.id

