#!/usr/bin/python3
import argparse
import os

class LatexCli:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Alphagens command line tool")
        self.subparsers = self.parser.add_subparsers(dest="command")


        self.subparsers.add_parser("clear", help="clear the outputs")

        # Define the "set" command
        set_parser = self.subparsers.add_parser("set", help="Set something")
        # ... add arguments for set ...

        # Define the "list" command
        list_parser = self.subparsers.add_parser("list", help="List items")
        # ... add arguments for list ...

        # Define the "create" command

        # create_parser = self.subparsers.add_parser("create", help="create the dependent files")

        # create_parser.add_argument("")

        run_parser = ...

        create_parser = self.subparsers.add_parser("create", help="create latex environment")
        
        # Add --type and --name arguments for install command

        create_parser.add_argument("path", 
                            type=str, 
                            help="Specify the path where item should be create")
        
        create_parser.add_argument("--title", 
                                    type=str, 
                                    required=True, 
                                    help="Specify the the title of pdf")
        
        create_parser.add_argument("--name", 
                                    type=str, 
                                    required=True, 
                                    help="Specify the name of pdf")

    def run(self):
        args = self.parser.parse_args()
        # Handle the arguments
        if args.command == "set":
            self.handle_set(args)
        elif args.command == "list":
            self.handle_list(args)
        elif args.command == "install":
            self.handle_install(args)
        elif args.command == "create":
            self.handle_create(args)
        elif args.command == "clear":
            self.handle_clear(args)
        else:
            self.parser.print_help()

    def handle_set(self, args):
        # Your set command implementation
        pass

    def handle_list(self, args):
        # Your list command implementation
        pass

    def handle_install(self, args):
        item_type = args.type
        item_name = args.name
        print(f"Installing {item_type}: {item_name}...")
        # ... Rest of your install command implementation ..

    def handle_create(self, args):
        latex = LatexGenerator(args.path, args.title, args.name)
        latex.deploy()
        print("hello")

    def handle_clear(self, args):
        os.system("rm -rf ./src")
        os.system("rm main.tex")
        os.system("rm main.pdf")
        os.system("rm Makefile")
        os.system("rm -rf ./build")

class LatexGenerator:
    main_include_packages = f"""\\documentclass[12pt]{{article}}

\\usepackage[UTF8]{{ctex}}

\\usepackage{{amsmath}}
\\usepackage{{amsthm}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{enumerate}}
\\usepackage{{fancyhdr}} 
\\usepackage{{tcolorbox}}
\\usepackage{{booktabs}} 
\\usepackage{{caption}} 
\\usepackage{{subcaption}}

% cumtom symbols
\\input{{./src/symbols.tex}}

% set page margin
\\setlength{{\\headheight}}{{15pt}}
\\geometry{{
a4paper,
top=2.5cm,
bottom=2.5cm,
left=2cm,
right=2cm
}}

% set header and footer
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{nanyi}}
\\lhead{{\\textrm{{homework}}}}
\\rfoot{{\\textrm{{Page}} \\thepage}}


\\begin{{document}}
    """


    main_ends = f"""
\\newpage
% \\bibliographystyle{{siam}}
% \\bibliography{{./src/references}}
\end{{document}}
    """

    symbols = f"""
% src/symbols.tex

% 重定义符号
\\newcommand{{\\R}}{{\mathbb{{R}}}} % 定义\R为实数集符号
"""
    
    Makefile = r"""
LATEX = xelatex
TARGET = main

all = start

start: $(TARGET)

$(TARGET): $(TARGET).tex
	@mkdir -p ./build
	@$(LATEX) -output-directory=./build $@.tex
	@bibtex ./build/$@.aux
	@$(LATEX) -output-directory=./build $@.tex
	@$(LATEX) -output-directory=./build $@.tex
	@ln -sf ./build/$@.pdf $@.pdf

restart:
	@make stop
	@make start

stop:
	@rm -rf ./build

clean:
	@rm -rf ./build
"""

    def __init__(self, path, title, name):
        self.path = os.path.normpath(path)
        self.title = title
        self.name = name

    def generate_infos(self):
        bb = f"""
\\title{{{self.title}}}
\\author{{{self.name}}}
\\date{{\\today}}
\\maketitle
        """
        return bb

    def deploy(self):
        
        print(f"generating {self.path}/main.tex")
        with open(f"{self.path}/main.tex", "w") as file:
            main_text = self.main_include_packages + self.generate_infos() + self.main_ends
            file.write(main_text)
        
        print(f"generating {self.path}/Makefile")
        with open(f"{self.path}/Makefile", "w") as file:
            text = self.Makefile
            file.write(text)
        
        print(f"running mkdir {self.path}/src")
        os.mkdir(f"{self.path}/src")

        print(f"generating {self.path}/src/symbols.tex")
        with open(f"{self.path}/src/symbols.tex", "w") as file:
            text = self.symbols
            file.write(text)
    
        print("successfully")

def main():
    cli = LatexCli()
    cli.run()

if __name__ == "__main__":
    main()