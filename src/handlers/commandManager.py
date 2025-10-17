import os
import importlib.util
<<<<<<< Updated upstream
import discord
from difflib import get_close_matches
=======
>>>>>>> Stashed changes

class commandManager:
    def __init__(self, client):
        self.Client = client

        self.PREFIX = '.'
        self.COMMANDPATH = 'src/commands/'

    def loadCommands(self):
        commands = {}
        for filename in os.listdir(self.COMMANDPATH):
            if filename.endswith('.py'):
                command_name = filename[:-3]
                command_file = os.path.join(self.COMMANDPATH, filename)
                spec = importlib.util.spec_from_file_location(command_name, command_file)
                command_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(command_module)
                commands[command_name] = command_module
        return commands

    def processCommand(self, message):
        command_body = message.content[len(self.PREFIX):].strip()
        command_parts = command_body.split()
        if len(command_parts) == 0 or command_parts[0] == '':
            return None
        command_name = command_parts[0]
        command_body = command_body[len(command_name):].strip()
        print(command_body)

        command_file = os.path.join(self.COMMANDPATH, f"{command_name}.py")
        # If no args provided for item lookup commands, show usage example instead of returning first item
        if command_name in ('talent', 'mantra', 'outfit', 'weapon', 'equipment') and len(command_args) == 0:
            usage_map = {
                'talent': '.talent {talent name}',
                'mantra': '.mantra {mantra name}',
                'outfit': '.outfit {outfit name}',
                'weapon': '.weapon {weapon name}',
                'equipment': '.equipment {equipment name}'
            }
            example = usage_map.get(command_name, f'.{command_name} {{name}}')
            embed = discord.Embed(title='Usage', description=f'Please provide an argument. Example: `{example}`', color=0xffcc00)
            return embed
        if os.path.isfile(command_file):
            spec = importlib.util.spec_from_file_location(command_name, command_file)
            command_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(command_module)

            if hasattr(command_module, 'execute'):
                return command_module.execute(command_body)
            else:
                print(f"Command {command_name} does not have an execute function.")
        else:
            # provide suggestions for mistyped commands (pluralization and fuzzy matches)
            available = [f[:-3] for f in os.listdir(self.COMMANDPATH) if f.endswith('.py')]
            # try singular/plural correction
            candidates = set(available)
            # naive plural->singular by stripping trailing 's' if present
            if command_name.endswith('s'):
                candidates.add(command_name[:-1])
            # fuzzy match
            close = get_close_matches(command_name, list(candidates), n=3, cutoff=0.6)
            suggestion_text = ''
            if close:
                suggestion_text = 'Perhaps you meant: ' + ', '.join(close)
            else:
                suggestion_text = f'Unknown command: {command_name}'

            embed = discord.Embed(title='Command not found', description=suggestion_text, color=0xffcc00)
            return embed