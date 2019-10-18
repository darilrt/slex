from ir_node import Node

class Variable(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.indexs = []
        self.type = None
        self.assign = None
        
        self.hide = False
        self.export = False

    def source(self, tab=""):
        if self.hide:
            return ""
        
        if self.cname == "":
            self.cname = self.name
        
        index = "".join(["[%s]" %self.irs.get_expr(e) for e in self.indexs])
        src = "%s %s%s" %(self.type[0], self.cname, index)
        
        if self.assign != None:
            src += " = " + self.get_expr(self.assign)
        
        return "%s%s;\n" %(tab, src)

    def header(self, tab=""):
        if self.hide:
                return ""
            
        if self.export:
            index = "".join(["[%i]" %self.get_expr(e) for e in self.indexs])
            return "export %s%s %s;\n" %(
                tab, self.type[0], self.cname
            )
        
        return ""

class Assign(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.expr = ""
        self.value = ""
    
    def source(self, tab=""):
        if self.cname == "":
            self.cname = self.name
        
        return "%s%s = %s;\n" %(tab, self.cname, self.get_expr(self.expr))
    