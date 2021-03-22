.PHONY = help clean vsopc

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make vsopc"
	@echo "To install tools type make install-tools"
	@echo "To know how to use the compiler vsopc: type ./vsopc -h"
	@echo "------------------------------------"

install-tools:
	@echo "installing tools ..."

vsopc:
	@echo "construction du compilateur"
	@echo "pour compiler un *.vsop type ./vsopc <path_of_*.vsop> on your terminal"
	@echo "#!/usr/bin/env python3" > vsopc
	@cat "main.py" >> "vsopc"
	@chmod +x vsopc

comp:
	@echo "archive made ..."
	@./make_archive.sh

runl:
	@python main.py -l test.vsop

runp:
	@python main.py -p test.vsop

clean:
	@echo "cleaned"
	@rm -f -r __pycache__
	@rm -f vsopc
	@rm -f -r .vscode
	@rm vsopcompiler.tar.xz