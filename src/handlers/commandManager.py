import os
import importlib.util
import discord

class commandManager:
    def __init__(self, client):
        self.Client = client

        self.PREFIX = '.'
        self.COMMANDPATH = 'src/commands/'

    def processCommand(self, message):
        content_lower = message.content.lower()
        if content_lower.startswith(self.PREFIX):
            command_body = message.content[len(self.PREFIX):].strip()
            command_parts = command_body.split()
            command_name = command_parts[0]
            command_args = command_parts[1:]

            command_file = os.path.join(self.COMMANDPATH, f"{command_name}.py")
            if os.path.isfile(command_file):
                spec = importlib.util.spec_from_file_location(command_name, command_file)
                command_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(command_module)

                if hasattr(command_module, 'execute'):
                    return command_module.execute(command_body)
                else:
                    print(f"Command {command_name} does not have an execute function.")
            else:
                print(f"Command file {command_file} not found.")