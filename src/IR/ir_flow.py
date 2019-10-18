from ir_node import Node
import IR

class If(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%sif (%s) {\n%s%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab
        )

class Elif(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%selse if (%s) {\n%s%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab
        )

class Else(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
    
    def source(self, tab=""):
        return "%selse {\n%s%s}\n" %(
            tab, self.childs_source(tab + "\t"), tab
        )

class Switch(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%sswitch (%s) {\n%s%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab
        )

class SwitchCase(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%scase %s: {\n%s%sbreak;\n%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab + "\t", tab
        )

class SwitchDefault(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
    
    def source(self, tab=""):
        return "%sdefault: {\n%s%sbreak;\n%s}\n" %(
            tab, self.childs_source(tab + "\t"), tab + "\t", tab
        )

class While(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%swhile (%s) {\n%s%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab
        )
