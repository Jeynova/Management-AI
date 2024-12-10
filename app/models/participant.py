class Participant:
    def __init__(self, name, email, ptype):
        self.name = name
        self.email = email
        self.ptype = ptype

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "type": self.ptype
        }