class Machine:
    """
    Representation of a machine in the cloud
    """
    def __init__(self,
                 id: str,
                 name: str,
                 public_ip: str=None):
        self.name = name
        self.id = id
        self.public_ip = public_ip