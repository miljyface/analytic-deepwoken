import os
import importlib.util
import discord
import plugins.dwbapi as dwb

class interactionManager:
    def __init__(self, client):
        self.Client = client
        self.COMMANDPATH = 'src/interactions/'

    def processReply(self, message):
        reply = message.content.strip()
        command_file = os.path.join(self.COMMANDPATH, f"{reply}.py")

        referenced = message.reference
        replied_msg = referenced.resolved
        link = replied_msg.content.split('https://deepwoken.co/builder?id=')[1].split()[0]
        build_id = link.split('&')[0]
        build = dwb.dwbBuild(build_id)

        if os.path.isfile(command_file):
            spec = importlib.util.spec_from_file_location(reply, command_file)
            command_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(command_module)

            if hasattr(command_module, 'execute'):
                return command_module.execute(build)
            else:
                print(f"Command {reply} does not have an execute function.")