from ir_node import Node
import IR

class Function(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.type = None
        self.args = []
        self.template = []
        self.constructor = False
        self.parent = None
        
        self.static = False
        self.virtual = False    
        self.operator = False    
	
    def push(self, node):
        if node.__class__ == IR.Variable:
            node.cname = "l_%s" %node.name
        
        self.childs.append(node)
        node.up = self
    
    def get_arg(self, e):
        e.hide = False
        s = e.source()[:-2]
        e.hide = True
        return s
    
    def source(self, tab=""):
        if self.cname == "" and not self.operator:
            self.cname = "f_" + self.name
            
            if self.name == "main":
                if self.parent == None:
                    self.cname = 'main'
        
        if self.virtual or self.operator:
            return ""
        
        px = ""
        if self.parent:
            px = "%s::" %self.parent.cname
        
        if len(self.template) > 0:
            return ""
        
        args = ", ".join([self.get_arg(e) for e in self.args])
        
        left = self.type[0]
        if self.static:
            left = "static " + left
        
        left += " " if left != "" else ""
        
        return "\n%s%s%s%s(%s) {\n%s%s}\n" %(
            tab, left, px, self.cname, args, self.childs_source(tab + "\t"), tab
        )
	
    def header(self, tab=""):
        if self.name == "main":
            if self.parent == None:
                return ""
                
        if self.cname == "" and not self.operator: self.cname = "f_" + self.name
        
        if len(self.template) > 0:
            tmp = ""
            args = ", ".join([self.get_arg(e) for e in self.args])
            
            name = self.cname
            if self.template[0] != None:
                
                tmp = ", ".join(["typename %s" %e['name'] for e in self.template])
                tmp = "%stemplate<%s>\n" %(tab, tmp)
                name = " " + name
            
            return "\n%s%s%s%s(%s) {\n%s%s}\n" %(
                tmp, tab, self.type[0], name, args,
                self.childs_source(tab + "\t"), tab
            )
        
        if self.operator:
            args = ", ".join([self.get_arg(e) for e in self.args])
            name, type = "", ""
            
            if self.name['__name__'] == "expr_op":
                name = self.name['op']
            
            return "%soperator %s(%s) {\n%s%s}\n" %(
                self.type[0], name, args,
                self.childs_source(tab + "\t"), tab
            )
        
        args = ", ".join([self.get_arg(e) for e in self.args])
        left = self.type[0]
        vr = ''
        
        if self.virtual:
            vr = " = 0"
            left = "virtual " + left
        
        if self.static:
            left = "static " + left
        
        left += " " if left != "" else ""
        
        return "\n%s%s%s(%s)%s;\n" %(tab, left, self.cname, args, vr)

class Call(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)

class Return(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.expr = None
        self.value = ""
    
    def source(self, tab=""):
        val = " " + self.get_expr(self.expr) if self.get_expr(self.expr) != "" else ""
        return "%sreturn%s;\n" %(tab, val)
