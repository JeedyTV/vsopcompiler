import sys
import argparse
from Lexer import make_token
from Parser import make_ast
#from aide import CalcParser

def extract_data(fichier):
    """
    remove the lf at the end of the files
    """
    data = ""
    temp = []
    
    for line in fichier:
        temp.append(line)

    while temp[-1] == "\n":
        temp.pop()

    for line in temp :
        data += line
    
    return data

def main():

    # Argument parser definition
    parser = argparse.ArgumentParser(description="Compiler for the VSOP language")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-lex', help='dump tokens on stdout', action='store_true')
    group.add_argument('-parse', help='dump parsed AST on stdout', action='store_true')
    parser.add_argument('source_file', help='path to the VSOP source file', type=str)

    args = parser.parse_args()

    # Checking if the input file is in vsop format
    if args.source_file.endswith(".vsop"): 

        try:

            with open(args.source_file, 'r') as file: 

                #clean the lfs at the end of the file and make a string contaning the vsop source code. 
                data = extract_data(file)
                
                #start of the synthax analyser , print token on stdout and error on stderr.
                
                if(args.lex):
                    make_token(data,args.source_file)
                if(args.parse):
                    make_ast(data,args.source_file)

                    
        
        except FileNotFoundError: # handle the case where the file does not exist.  
            print("vsop: can't open file '"+str(args.source_file)+"': No such file or directory", file=sys.stderr)
        
    else: # handle the case where the file has the wrong extension
        print("vsop: can't handle file '"+str(args.source_file)+"': Wrong file format", file=sys.stderr)

if __name__ == '__main__':
    main()