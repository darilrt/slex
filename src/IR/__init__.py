from ir_node import Null, Node, File, Package, Line, Type, TypeDef, Expr, Cpp, Hpp
from ir_class import Class
from ir_function import Function, Call, Return
from ir_variable import Variable, Assign
from ir_flow import If, Elif, Else, Switch, SwitchCase, SwitchDefault, While#, For
from ir_scanner import Scanner
from ir_package import *

class List:
    def __init__(self):
        self.irs = irs
        self.list = []
        
    def push(self, node):
        self.list.append(node)
    
    def _get_name(self, node):
        return t.cname, t
    
    def get_name(self):
        lst = [[l.cname, l.__class__] for l in self.list]
        
        name = ""
        for n in lst:
            name += n[0]
            
            if n != lst[-1:]:
                if n[1] == Package:
                    name += "::"
            
            if n[1] != Class and n[1] != Type:
                self.irs.fatal("TypeError", "\"%s\" is not datatype" %n[0])
        
        return name, lst