from eventcommand import get_command

class EventFunction:

    def __init__(self):
        self.data = bytearray()
        self.commands = []
        self.offsets = []

        self.pos = 0

    def from_bytearray(func_bytes: bytearray):
        ret = EventFunction()

        pos = 0
        while pos < len(func_bytes):
            cmd = get_command(func_bytes, pos)
            ret.add(cmd)
            pos += len(cmd)

        return ret

    def add(self, event_command):
        self.commands.append(event_command)
        self.offsets.append(self.pos)
        self.pos += len(event_command)
        self.data.extend(event_command.to_bytearray())

        return self

    def set_label(self, label: str):
        pass

    def branch(self, branch_command):
        pass

    def __str__(self):
        ret = ''
        for i in range(len(self.commands)):
            ret += (f"[{self.offsets[i]:04X}]" + str(self.commands[i]))
            ret += '\n'

        return ret

    def get_bytearray(self):
        return self.data
