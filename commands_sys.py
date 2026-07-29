class CommandSystem:
    def __init__(self, logger):
        self.commands = {}
        self.logger = logger

    def register(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

    def execute(self, cmd):
        cmd = cmd.lower().strip()

        parts = cmd.split()
        if not parts:
            return

        args = []

        for i in range(len(parts), 0, -1):
            possible_cmd = " ".join(parts[:i])

            if possible_cmd in self.commands:
                command = possible_cmd
                args = parts[i:]
                break
        else:
            print("Unknown command. Type 'help'")
            return

        try:
            self.commands[command](args)
        except Exception as e:
            self.logger.error(f"Error: {e}")
