import argparse

class alphagensClient:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Alphagens command line tool")
        self.subparsers = self.parser.add_subparsers(dest="command")
        self.parser.register
        # Define the "clear" command
        clear_parser = self.subparsers.add_parser("clear", help="clear the outputs")
        # Define the "set" command
        set_parser = self.subparsers.add_parser("set", help="Set something")
        # ... add arguments for set ...
        # Define the "list" command
        list_parser = self.subparsers.add_parser("list", help="List items")
        # ... add arguments for list ...
        # Define the "create" command
        
        # create_parser = self.subparsers.add_parser("create", help="create the dependent files")
        # create_parser.add_argument("")

        create_parser = self.subparsers.add_parser("create", help="create latex environment")
        create_parser.add_argument("path", type=str, help="Specify the path where item should be create")
        create_parser.add_argument("--title", type=str, required=True, help="Specify the the title of pdf")
        create_parser.add_argument("--name", type=str, required=True, help="Specify the name of pdf")
        
    def run(self):
        args = self.parser.parse_args()
        pass
