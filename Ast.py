import sys

"""
all the classes below are node of the ast.
"""

class literal():

    def __init__(self,value):
        self.value = value

    def display(self):
        sys.stdout.write(str(self.value))

class args():

    def __init__(self):
        self.expr = []
    
    def display(self):
        sys.stdout.write('[')
        for i,expr in enumerate(self.expr):
            expr.display()
            if i != len(self.expr) -1:
                sys.stdout.write(', ')
        sys.stdout.write("]")

class par():
    
    def __init__(self,value):
        self.value = value
    
    def display(self):
        sys.stdout.write(self.value)

class self_():

    def __init__(self):
        pass
    
    def display(self):
        sys.stdout.write('self')

class obj_id():

    def __init__(self,type_):
        self.type_ = type_
        
    def display(self):
        sys.stdout.write(self.type_)

class new():

    def __init__(self,type_name):
        self.type_name = type_name

    def display(self):
        sys.stdout.write('New({})'.format(self.type_name))

class call():

    def __init__(self,obj_expr,methode_name,args):
        self.obj_expr = obj_expr
        self.methode_name = methode_name
        self.args = args

    def display(self):
        sys.stdout.write('Call(')
        self.obj_expr.display()
        sys.stdout.write(', '+self.methode_name+', ')
        self.args.display()
        sys.stdout.write(') ')

class unary():

    def __init__(self,type_,expr):
        self.type_ = type_
        self.expr = expr

    def display(self):
        sys.stdout.write('UnOp('+self.type_+', ')
        self.expr.display()
        sys.stdout.write(') ')

class binary():

    def __init__(self,type_,expr1,expr2):
        self.type_ = type_
        self.expr1 = expr1
        self.expr2 = expr2
    
    def display(self):
        sys.stdout.write('BinOp('+self.type_+', ')
        self.expr1.display()
        sys.stdout.write(', ')
        self.expr2.display()
        sys.stdout.write(') ')

class assign():

    def __init__(self,name,expr):
        self.name = name
        self.expr = expr
    
    def display(self):
        sys.stdout.write('Assign('+self.name+(', '))
        self.expr.display()
        sys.stdout.write(') ')

class let():

    def __init__(self,name,type_,init_expr,scope_expr):
        self.name = name
        self.type_ = type_
        self.init_expr = init_expr
        self.scope_expr = scope_expr
    
    def display(self):
        if self.init_expr == None:
            sys.stdout.write('Let('+self.name+', '+self.type_+', ')
            self.scope_expr.display()
            sys.stdout.write(') ')
        else:
            sys.stdout.write('Let('+self.name+', '+self.type_+', ')
            self.init_expr.display()
            sys.stdout.write(', ')
            self.scope_expr.display()
            sys.stdout.write(') ')

class while_():

    def __init__(self,cond_expr,body_expr):
        self.cond_expr = cond_expr
        self.body_expr = body_expr

    def display(self):
        sys.stdout.write('While(')
        self.cond_expr.display()
        sys.stdout.write(', ')
        self.body_expr.display()
        sys.stdout.write(') ')

class if_():

    def __init__(self,cond_expr,then_expr,else_expr):
        self.cond_expr = cond_expr 
        self.then_expr = then_expr
        self.else_expr = else_expr
    
    def display(self):
        if self.else_expr == None:
            sys.stdout.write('If(')
            self.cond_expr.display()
            sys.stdout.write(', ')
            self.then_expr.display()
            sys.stdout.write(') ')
        else:
            sys.stdout.write('If(')
            self.cond_expr.display()
            sys.stdout.write(', ')
            self.then_expr.display()
            sys.stdout.write(', ')
            self.else_expr.display()
            sys.stdout.write(') ')

class block():

    def __init__(self):
        self.exprs = []
    
    def display(self):
        sys.stdout.write('[')
        for i,expr in enumerate(self.exprs):
            expr.display()
            if i != len(self.exprs) -1:
                sys.stdout.write(', ')
        sys.stdout.write('] ')

class formals():

    def __init__(self):
        self.formal = []
    
    def display(self):
        sys.stdout.write('[')
        for i,expr in enumerate(self.formal):
            expr.display()
            if i != len(self.formal) -1:
                sys.stdout.write(', ')
        sys.stdout.write('] ')

class formal():

    def __init__(self,name,type_):
        self.name = name
        self.type_ = type_
    
    def display(self):
        sys.stdout.write('{} : {}'.format(self.name,self.type_))
    
class method():

    def __init__(self,name,formals,ret_type,block):
        self.name = name
        self.formals = formals
        self.ret_type = ret_type
        self.block = block

    def display(self):
        sys.stdout.write('Method({}, '.format(self.name))
        self.formals.display()
        sys.stdout.write(', ')
        sys.stdout.write(self.ret_type)
        sys.stdout.write(', ')
        self.block.display()
        sys.stdout.write(') ')

class field():

    def __init__(self,name,type_,init_expr):
        self.name = name
        self.type_ = type_
        self.init_expr = init_expr

    def display(self):
        if self.init_expr == None:
            sys.stdout.write('Field({}, {}'.format(self.name,self.type_))
        else:
            sys.stdout.write('Field({}, {}'.format(self.name,self.type_))
            sys.stdout.write(', ')
            self.init_expr.display()
        
        sys.stdout.write(') ')

class class_body():

    def __init__(self):
        self.fields = []
        self.methods = []
    
    def display(self):
        sys.stdout.write('[')
        for i,expr in enumerate(self.fields):
            expr.display()
            if i != len(self.fields) -1:
                sys.stdout.write(', ')
        sys.stdout.write('] ')
        sys.stdout.write(', ')
        sys.stdout.write('[')
        for i,expr in enumerate(self.methods):
            expr.display()
            if i != len(self.methods) -1:
                sys.stdout.write(', ')
        sys.stdout.write('] ')

class class_():

    def __init__(self,name,parent,class_body):
        self.name = name
        self.parent = parent
        self.class_body = class_body

    def display(self):
        if self.parent is None:
            sys.stdout.write('Class({}, Object, '.format(self.name))
            self.class_body.display()
            sys.stdout.write(') ')
        else:
            sys.stdout.write('Class({}, {}, '.format(self.name,self.parent))
            self.class_body.display()
            sys.stdout.write(') ')

class program():

    def __init__(self):
        self.classes = []

    def display(self):
        sys.stdout.write('[')
        for i,expr in enumerate(self.classes):
            expr.display()
            if i != len(self.classes) -1:
                sys.stdout.write(', ')
        sys.stdout.write(']\n')
