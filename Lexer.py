from sly import Lexer
import sys
import re

class CalcLexer(Lexer):

    def __init__(self,sourceCode,sourceCodeName):
        self.sourceCode = sourceCode
        self.sourceCodeName = sourceCodeName
        self.single_line_com = False #state of the lexer
        self.multiple_line_com = list() #state of the lexer
        self.string_unfinish = False
    
    #define the tokens accepted by the lexer
    tokens = {STRING_LITERAL, INTEGER_LITERAL, TYPE_IDENTIFIER, OBJECT_IDENTIFIER}
    
    #handle string correctly
    def handleStringLit(self,value,line,column):

        #in case or error
        error_line = value.count('\\\n', 0, len(value))
        tab_line_fine_handle = value.split("\\\n")
        
        # Removing \\\n, \t, \b and \r from the original string
        value = re.sub(r'(\\\n([\t\b\r ])*|\\\n)', '', value)
        
        # Checking the validity of the string
        if '\n' in value:
            for bad in tab_line_fine_handle:
                if '\n' in bad:
                    erro_column = bad.rfind('\n', 0, len(bad)) +1
            self.print_error(self.sourceCodeName,line+error_line,erro_column,"String contains line feed without backslash")
        
        if value.rfind('\\', 0, len(value))+2 == len(value):
            self.print_error(self.sourceCodeName,line,column+value.rfind('\\', 0, len(value)),"String contains backslash without linefeed or escape character")
        
        accept = ['b','t','n','r','"',r'\\','x']
        if ('\\' in value) :
            after = value[value.rfind('\\', 0, len(value))+1]
            if after not in accept:
                self.print_error(self.sourceCodeName,line,column+value.rfind('\\', 0, len(value)),"String contains backslash without linefeed or escape character")

        if '\\x00' in value:
            self.print_error(self.sourceCodeName,line,column+value.rfind('\\x00', 0, len(value)),"String contains null character")
        
        # Replacing escape characters into hexadecimals

        value = value.replace(r'\b', r'\x08')
        value = value.replace(r'\t', r'\x09')
        value = value.replace(r'\n', r'\x0a')
        value = value.replace(r'\r', r'\x0d')
        value = value.replace(r'\"', r'\x22')
        value = value.replace(r'\\', r'\x5c')

        

        for c in value:

            # Replacing characters that aren't in the range(32, 127)...
            if not(32 <= ord(c) and ord(c) <= 127):
                hexa = hex(ord(c))[2::]

                # ... into hexadecimals
                if len(hexa) == 1:
                    value = value.replace(c, '\\x0'+str(hexa))
                else:
                    value = value.replace(c, '\\x'+str(hexa))
        
        

        # Getting "\" posistion(s) in the string 
        escaped_index = [m.start() for m in re.finditer(r'\\', value)]
        
        for index in escaped_index:

            # Checking the char after '\'
            if value[index + 1] == 'x':
                hex_value = value[index + 2:index + 4]
                
                try: 
                    int('0x'+str(hex_value), 0)

                except ValueError: 
                    self.print_error(self.sourceCodeName,line,column+index,"Not a valid hexadecimal expression in back of \\")
                    break
                
            else:
                self.print_error(self.sourceCodeName,line,column+index,"String contains backslash without any valid hexadecimal number or escape character")
        
        return value
    
    def in_line_comment(self):
        #renvoie true if single comment 
        return self.single_line_com
    
    def in_multiple_comment(self):
        #renvoie true if multiple comments
        return not (len(self.multiple_line_com) == 0)
    
    def in_comment(self):
        #renvoie true if in comment
        return self.in_line_comment() or self.in_multiple_comment()

    @_(r'\/\/')
    def COM(self, t):

        if not self.in_comment(): #if we are not in single comment state pass in single comment state
            self.single_line_com = True
        
    @_(r'\(\*')
    def COMIN(self, t):

        if not self.in_line_comment(): #if we are not in single comment state pass in multiple-comment state
            self.multiple_line_com.append((self.lineno,self.find_column(self.sourceCode,t))) # to print error correctly
            
    @_(r'\*\)')
    def COMOUT(self, t):

        t.type = "COMOUT " +str(len(self.multiple_line_com)) #remind the nested level
        
        if not self.in_line_comment(): #if we are not in single comment state handle properly

            if not self.in_multiple_comment(): #if we are not in multiple comment state it's an error
                self.print_error(self.sourceCodeName,self.lineno,self.find_column(self.sourceCode,t),"*) doesn't match to a (*.")
            else:
                self.multiple_line_com.pop()
    
    # String containing ignored characters
    ignore_tab = '\t'
    ignore = ' ' 
    
    @_(r'!|`')
    def EX(self,t):
        if not (self.in_comment()):
            self.print_error(self.sourceCodeName,self.lineno,self.find_column(self.sourceCode,t),"Bad character : "+str(t.value[0]))

    @_(r'\"(?:[^\"\\]|\\.|\\\n)*\"')
    def STRING_LITERAL(self,t):
        
        self.lineno += t.value.count("\\\n")
        t.value = self.handleStringLit(t.value,t.lineno,self.find_column(self.sourceCode,t))
        if not self.in_comment(): #if in comment state droped the token
            if not self.string_unfinish: #if an string unfinish error is raised do not create token
                return t
    
    @_(r'\"(?:[^\"\\\(\*\*\)\n]|\\.|\\\n)*\n',
    r'\"(?:[^\"\\\(\*\*\)]|\\.|\\\n)*')
    def STRING_LITERAL_UNFINISH(self,t):
        
        in_comment = self.in_comment()
        # update line if needed
        self.lineno += t.value.count("\\\n")
        if t.value.endswith("\n") > 0:
            self.lineno += 1
        
            if not self.in_multiple_comment():
                self.single_line_com = False
        
        if not in_comment: #if in comment state droped the token
            self.string_unfinish = True #if it's an string unfinish change state of the lexer
            self.handleStringLit(t.value,t.lineno,self.find_column(self.sourceCode,t))
            self.print_error(self.sourceCodeName,t.lineno,self.find_column(self.sourceCode,t),"EOF in a string")

    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECT_IDENTIFIER(self,t):
        
        if(t.value == 'and'):
            t.type = "AND"
        if(t.value == 'bool'):
            t.type =  "BOOL"
        if(t.value == 'class'):
            t.type = "CLASS"
        if(t.value == 'do'):
            t.type = "DO"
        if(t.value == 'else'):
            t.type = "ELSE" 
        if(t.value == 'extends'):
            t.type = "EXTENDS"
        if(t.value == 'false'):
            t.type = "FALSE"
        if(t.value == 'if'):
            t.type = "IF"
        if(t.value == 'int32'):
            t.type = "INT32"
        if(t.value == 'in'):
            t.type = "IN"
        if(t.value == 'isnull'):
            t.type = "ISNULL"
        if(t.value == 'let'):
            t.type = "LET"
        if(t.value == 'new'):
            t.type = "NEW"
        if(t.value == 'not'):
            t.type = "NOT"
        if(t.value == 'self'):
            t.type = "SELF"
        if(t.value == 'string'):
            t.type = "STRING"
        if(t.value == 'then'):
            t.type = "THEN"
        if(t.value == 'true'):
            t.type = "TRUE"
        if(t.value == 'unit'):
            t.type = "UNIT"
        if(t.value == 'while'):
            t.type = "WHILE"
        
        """
        if in comment state droped the token or 
        if an string unfinish error is raised do not create token
        """
        if not self.in_comment() and not self.string_unfinish:
            return t
    
    @_(r'[A-Z][a-zA-Z0-9_]*')
    def TYPE_IDENTIFIER(self,t):
        """
        if in comment state droped the token or 
        if an string unfinish error is raised do not create token
        """
        if not self.in_comment() and not self.string_unfinish:
            return t

    @_(r'0x[0-9a-zA-Z]+',
    r'[0-9][0-9a-zA-Z]*')
    def INTEGER_LITERAL(self, t):
        
        in_comment = self.in_comment()
        
        if t.value.startswith('0x'):
            try :
                t.value = int(t.value[2:], 16)
            except ValueError:
                if not in_comment:
                    self.print_error(self.sourceCodeName,self.lineno,self.find_column(self.sourceCode,t),"Can't convert {"+str(t.value)+"} in hexadecimal.")
                
        else:
            try:
                t.value = int(t.value)
            except ValueError:
                if not in_comment:
                    self.print_error(self.sourceCodeName,self.lineno,self.find_column(self.sourceCode,t),"Can't convert {"+str(t.value)+"} in integer.")
                
        """
        if in comment state droped the token or 
        if an string unfinish error is raised do not create token
        """
        
        if not in_comment and not self.string_unfinish:
            return t
    
    @_(r'<=|<-|\{|\}|\(|\)|:|;|,|\+|-|\*|/|\^|\.|=|<')
    def OP(self,t):
        
        if(t.value == '<=') :
            t.type = "LOWER_EQUAL"
        if(t.value == '<-') :
            t.type = "ASSIGN"
        if(t.value =='{'):
            t.type = "LBRACE"
        if(t.value =='}'):
            t.type = "RBRACE" 
        if(t.value =='('):
            t.type = "LPAR"  
        if(t.value ==')'):
            t.type = "RPAR"  
        if(t.value ==':'):
            t.type = "COLON"  
        if(t.value ==';'):
            t.type = "SEMICOLON"  
        if(t.value ==','):
            t.type = "COMMA"  
        if(t.value =='+'):
            t.type = "PLUS" 
        if(t.value =='-'):
            t.type = "MINUS"
        if(t.value =='*'):
            t.type = "TIMES"
        if(t.value =='/'):
            t.type = "DIV"
        if(t.value =='^'):
            t.type = "POW"  
        if(t.value =='.'):
            t.type = "DOT"  
        if(t.value =='='):
            t.type = "EQUAL"  
        if(t.value =='<'):
            t.type = "LOWER"  
        
        """
        if in comment state droped the token or 
        if an string unfinish error is raised do not create token
        """
        
        if not self.in_comment() and not self.string_unfinish:
                return t

    def error(self, t):
        self.print_error(self.sourceCodeName,self.lineno,self.find_column(self.sourceCode,t),"Bad character : "+str(t.value[0]))

    @_(r'\n+')
    def ignore_newline(self, t):
        #update line of tokens
        self.lineno += t.value.count('\n')
        
        #quit single line mode if needed i.e if we are not in multiple line state
        if not self.in_multiple_comment():
            self.single_line_com = False

    def find_column(self,text, token):
        
        last_cr = text.rfind('\n', 0, token.index) + 1
        column = (token.index - last_cr) + 1
        
        return column
    
    def print_error(self,filename,line,column,description):
        #Print the error on the stderr in the good format
        sys.exit('{}:{}:{}: lexical error: {}'.format(filename, line, column, description))

def make_token(sourceCode,sourceCodeName):
        """
        make tokens of the source code and print on stdout print error if any on stderr
        """
        lexer = CalcLexer(sourceCode,sourceCodeName)
        
        for token in lexer.tokenize(sourceCode):
            
            token_line = token.lineno
            token_column = lexer.find_column(sourceCode,token)
            token_class = token.type.replace("_", "-").lower()
            
            if (token.type == "TYPE_IDENTIFIER" or token.type == "OBJECT_IDENTIFIER" or 
            token.type == "INTEGER_LITERAL" or token.type == "STRING_LITERAL"):
                token_value = token.value
            
            else :
                token_value = None
            
            if token_value == None:
                print(token_line,token_column,token_class,sep=",")
                pass
            else :
                print(token_line,token_column,token_class,token_value,sep=",")
                pass
            
        #chech wether the comment trigger an error or not

        if(len(lexer.multiple_line_com) != 0):
            lexer.print_error(sourceCodeName,lexer.multiple_line_com[-1][0],lexer.multiple_line_com[-1][1],"EOF in multiple line comment")
