"""Worker interface scaffold for the next RED cycle."""
def run_once(store, clock, transport):
    return 0


class SMTPTransport:
    def __init__(self, host, port, sender, starttls=True, username=None, password=None):
        self.host,self.port,self.sender=host,port,sender
        self.starttls,self.username,self.password=starttls,username,password

    def send(self,kind,payload):
        pass
