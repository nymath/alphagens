import argparse
import os
from pathlib import Path

class alphagensClient:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Alphagens command line tool")

        self.subparsers = self.parser.add_subparsers(dest="command")

        # Define the "clear" command
        clear_parser = self.subparsers.add_parser("clear", help="clear the outputs")
        # Define the "init" command
        init_parser = self.subparsers.add_parser("init", help="initilize")
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
        # Handle the arguments
        if args.command == "init":
            self.handle_init(args)
        else:
            self.parser.print_help()

    def handle_init(self, args):
        main_path = os.path.expanduser("~")
        alphagens_path = os.path.join(main_path, ".alphagens")
        data_path = os.path.join(alphagens_path, "data")
        os.mkdir(alphagens_path)
        os.mkdir(data_path)


