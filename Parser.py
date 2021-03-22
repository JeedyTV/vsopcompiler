from sly import Parser
from Lexer import CalcLexer
from Ast import *

class CalcParser(Parser):
    
    #define all the tokens used in the grammar
    tokens = CalcLexer.tokens
    more_tokens = {AND, BOOL, CLASS, DO, ELSE, EXTENDS, FALSE, IF, INT32, IN,
    ISNULL, LET, NEW, NOT, SELF, STRING, THEN, TRUE, UNIT, WHILE,
    LOWER_EQUAL, ASSIGN, LBRACE, RBRACE, LPAR, RPAR, COLON,
    SEMICOLON, COMMA, PLUS, MINUS, TIMES, DIV, POW, DOT, EQUAL, 
    LOWER}
    tokens = tokens | more_tokens
    #end of the define

    def __init__(self,sourceCode,sourceCodeName):
        self.stack = list()
        self.state_error = False
        self.sourceCode = sourceCode
        self.sourceCodeName = sourceCodeName

    # This sets the order of execution. The last values will have a higher precedence
    precedence = (
        ('right', 'ASSIGN'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('nonassoc', 'LOWER', 'LOWER_EQUAL', 'EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV'),
        ('right', 'ISNULL'),
        ('right', 'POW'),
        ('left', 'DOT'),
    )

    start = 'program'

    """
    the following implement all the grammar 
    and make the ast at the same time
    """

    @_('class_ { class_ }')
    def program(self,p):
        """
        implemented the following rule:
        program = class { class };
        """
        nbr_class = 1+len(p[1])
        pr = program()
        
        while nbr_class > 0:
            pr.classes.append(self.stack.pop(-nbr_class))
            nbr_class-=1
        
        return pr
        
    @_('CLASS TYPE_IDENTIFIER [ EXTENDS TYPE_IDENTIFIER ] class_body')
    def class_(self,p):
        """
        implemented the following rule:
        class = "class" type-identifier [ "extends" type-identifier ] class-body;
        """
        c = class_(p[1],p[2][1],self.stack.pop())
        self.stack.append(c)
    
    @_('LBRACE { field|method  } RBRACE')
    def class_body(self,p):
        """
        implemented the following rule:
        class-body = "{" { field | method } "}";
        """
        nbr_field_and_method = len(p[1])
        cb = class_body() 
        while nbr_field_and_method > 0:
            if len(self.stack) > 0 and type(self.stack[-nbr_field_and_method]) is field:
                cb.fields.append(self.stack.pop(-nbr_field_and_method))
            elif len(self.stack) > 0 and type(self.stack[-nbr_field_and_method]) is method:
                cb.methods.append(self.stack.pop(-nbr_field_and_method))
            nbr_field_and_method -= 1
        
        self.stack.append(cb)
        
    @_('OBJECT_IDENTIFIER COLON type_ [ ASSIGN expr ] SEMICOLON')
    def field(self,p):
        """
        implemented the following rule:
        field = object-identifier ":" type [ "<-" expr ] ";";
        """
        
        if '<-' in p[3]:
            expr = self.stack.pop()
            type_ = self.stack.pop()
            f = field(p[0],type_,expr)
        else:
            type_ = self.stack.pop()
            f = field(p[0],type_,None)
        
        self.stack.append(f)
        
    @_('OBJECT_IDENTIFIER LPAR [ formals ] RPAR COLON type_ block')
    def method(self,p):
        """
        implemented the following rule:
        method = object-identifier "(" formals ")" ":" type block;
        """

        if len(self.stack) > 2 and type(self.stack[-3]) is formals:
            b = self.stack.pop()
            type_ = self.stack.pop()
            f = self.stack.pop()
            m = method(p[0],f,type_,b)
        else:
            b = self.stack.pop()
            type_ = self.stack.pop()
            m = method(p[0],formals(),type_,b)
        
        self.stack.append(m)
    
    @_('TYPE_IDENTIFIER','INT32','BOOL','STRING','UNIT')
    def type_(self,p):
        """
        implemented the following rule:
        type = type-identifier | "int32" | "bool" | "string" | "unit";
        """
        self.stack.append(p[0])
    
    @_('formal { COMMA formal }')
    def formals(self,p):
        """
        implemented the following rule:
        formals = [ formal { "," formal } ];
        """
        nbr_formal = 1+len(p[1])
        f = formals()
        while nbr_formal > 0:
            f.formal.append(self.stack.pop(-nbr_formal))
            nbr_formal -=1
        
        self.stack.append(f)
    
    @_('OBJECT_IDENTIFIER COLON type_')
    def formal(self,p):
        """
        implemented the following rule:
        formal = object-identifier ":" type;
        """
        f = formal(p[0],self.stack.pop())
        self.stack.append(f)
    
    @_('LBRACE expr { SEMICOLON expr } RBRACE')
    def block(self,p):
        """
        implemented the following rule:
        block = "{" expr { ";" expr } "}";
        """
        nbr_expr = 1+len(p[2])
        b = block()
        while nbr_expr >0:
            b.exprs.append(self.stack.pop(-nbr_expr))
            nbr_expr -= 1
        
        self.stack.append(b)
    
    @_('IF expr THEN expr [ ELSE expr ]')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "if" expr "then" expr [ "else" expr ]
        """
        
        if 'else' in p[-1]:
            else_expr = self.stack.pop()
            then_expr = self.stack.pop()
            cond_expr = self.stack.pop()
            i = if_(cond_expr,then_expr,else_expr)
        else:
            then_expr = self.stack.pop()
            cond_expr = self.stack.pop()
            i = if_(cond_expr,then_expr,None)
        
        self.stack.append(i)
            
    @_('WHILE expr DO expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "while" expr "do" expr
        """
        
        expr_body = self.stack.pop()
        expr_cond = self.stack.pop()

        w = while_(expr_cond,expr_body)

        self.stack.append(w)
    
    @_('LET OBJECT_IDENTIFIER COLON type_ [ ASSIGN expr ] IN expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "let" object-identifier ":" type [ "<-" expr ] "in" expr
        """
        
        if '<-' in p[4]:
            expr_in = self.stack.pop()
            expr_ass = self.stack.pop()
            type_ = self.stack.pop()
            l = let(p[1],type_,expr_ass,expr_in)
        else:
            expr = self.stack.pop()
            type_ = self.stack.pop()
            l = let(p[1],type_,None,expr)

        self.stack.append(l)
        
    @_('OBJECT_IDENTIFIER ASSIGN expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = object-identifier "<-" expr
        """
        ass = assign(p[0],self.stack.pop())
        self.stack.append(ass)
    
    @_('NOT expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "not" expr
        """
        not_ = unary('not',self.stack.pop())
        self.stack.append(not_)
    
    @_('expr AND expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr "and" expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('and',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr LOWER_EQUAL expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("=" | "<" | "<=") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('<=',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr LOWER expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("=" | "<" | "<=") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('<',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr EQUAL expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("=" | "<" | "<=") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('=',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr MINUS expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("+" | "-") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('-',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr PLUS expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("+" | "-") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('+',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr DIV expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("*" | "/") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('/',exp1,exp2)
        self.stack.append(binop)

    @_('expr TIMES expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr ("*" | "/") expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('*',exp1,exp2)
        self.stack.append(binop)
    
    @_('expr POW expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr "^" expr
        """
        exp2 = self.stack.pop()
        exp1 = self.stack.pop()
        binop = binary('^',exp1,exp2)
        self.stack.append(binop)

    @_('MINUS expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "-" expr
        """
        minus = unary('-',self.stack.pop())
        self.stack.append(minus)
    
    @_('ISNULL expr')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "isnull" expr
        """
        is_null = unary('isnull',self.stack.pop())
        self.stack.append(is_null)

    @_('OBJECT_IDENTIFIER LPAR [ args ] RPAR')
    def expr(self,p):
        """
        implemented the following rule:
        expr = object-identifier "(" args ")"
        """
        if type(self.stack[-1]) is args:
            c = call(self_(),p[0],self.stack.pop())
        else:
            c = call(self_(),p[0],args())
        
        self.stack.append(c)
    
    @_('expr DOT OBJECT_IDENTIFIER LPAR [ args ] RPAR')
    def expr(self,p):
        """
        implemented the following rule:
        expr = expr "." object-identifier "(" args ")"
        """
        
        if type(self.stack[-1]) is args:
            args_ = self.stack.pop()
            m_name = self.stack.pop()
            c = call(m_name,p[2],args_)
        else:
            m_name = self.stack.pop()
            c = call(m_name,p[2],args()) 
        
        self.stack.append(c)
    
    @_('NEW TYPE_IDENTIFIER')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "new" type-identifier
        """
        n = new(p[1])
        self.stack.append(n)
    
    @_('OBJECT_IDENTIFIER')
    def expr(self,p):
        """
        implemented the following rule:
        expr = object-identifier
        """
        o = obj_id(p[0])
        self.stack.append(o)

    @_('SELF')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "self"
        """
        s = self_()
        self.stack.append(s)

    @_('literal')
    def expr(self,p):
        """
        implemented the following rule:
        expr = literal
        """
        pass
    
    @_('LPAR RPAR')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "(" ")"
        """
        p = par('()')
        self.stack.append(p)
 
    @_('LPAR expr RPAR')
    def expr(self,p):
        """
        implemented the following rule:
        expr = "(" expr ")"
        """
        pass
    
    @_('block')
    def expr(self,p):
        """
        implemented the following rule:
        expr = block;
        """
        pass

    @_('expr { COMMA expr } ')
    def args(self,p):
        """
        implemented the following rule:
        args = [ expr { "," expr } ];
        """
        nbr_expr = 1+len(p[1])
        args_ = args()
        
        while nbr_expr >0:
            args_.expr.append(self.stack.pop(-nbr_expr))
            nbr_expr -= 1
        
        self.stack.append(args_)

    @_('INTEGER_LITERAL','STRING_LITERAL','boolean_literal')
    def literal(self, p):
        """
        implemented the following rule:
        literal = integer-literal | string-literal | boolean-literal;
        """
        if (type(p[0]) is int)or (type(p[0]) is str):
            l = literal(p[0])
            self.stack.append(l)
        
    @_('TRUE','FALSE')
    def boolean_literal(self,p):
        """
        implemented the following rule:
        boolean-literal = "true" | "false";
        """
        l = literal(p[0])
        self.stack.append(l)
    
    def find_column(self,text, token):
        """find column of a token"""
        last_cr = text.rfind('\n', 0, token.index) + 1
        column = (token.index - last_cr) + 1
        
        return column

    def error(self,p):
        """detect an error and print it on stderr 
            don't have the time to be more specific on it.
        """
        if p != None:
            line = p.lineno
            column = self.find_column(self.sourceCode,p)
            self.print_error(self.sourceCodeName,line,column)
        else :
            line = self.sourceCode.count('\n') + 2
            column = 1
            self.print_error(self.sourceCodeName,line,column)
    
    def print_error(self,filename,line,column):
        #Print the error on the stderr in the good format
        sys.exit('{}:{}:{}: syntax error'.format(filename, line, column))

def make_ast(data,source_file):
    """
    instantiate the parser and dump the ast on the stdout
    """
    lexer = CalcLexer(data,source_file)
    parser = CalcParser(data,source_file)
    ast = parser.parse(lexer.tokenize(data))

    if(len(lexer.multiple_line_com) != 0):
        lexer.print_error(source_file,lexer.multiple_line_com[-1][0],lexer.multiple_line_com[-1][1],"EOF in multiple line comment")
    
    if not parser.state_error:
        ast.display()
    else:
        exit(1)