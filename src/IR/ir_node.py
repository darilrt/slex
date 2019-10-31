class Null:
    pass

class Node:
    def __init__(self, name="", type=None):
        self._type 	= type
        self.irs 	= None
        self.name	= name
        self.up     = None
        self.childs = []
        self.all_props = False
        self._stack_context = []
    
    def set_context(self, lst):
        self._stack_context = map(lambda x: x, lst)
    
    def set_current_context(self):
        self.set_context(self.irs._stack_current)
    
    def get_type(self, o):
        stack = self.irs._stack_current
        
        self.irs._stack_current = self._stack_context
        n = self.irs.get_type(o)
        self.irs._stack_current = stack
        return n
    
    def get_expr(self, o):
        stack = self.irs._stack_current
        
        self.irs._stack_current = self._stack_context
        n = self.irs.get_expr(o)
        self.irs._stack_current = stack
        return n
    
    def get_dotted(self, o):
        stack = self.irs._stack_current
        
        self.irs._stack_current = self._stack_context
        n = self.irs.get_dotted(o)
        self.irs._stack_current = stack
        return n
    
    def find(self, type, name):
        for child in self.childs:
            if child.__class__ == type and child.name == name:
                return child

    def exists(self, name):
        for child in self.childs:
            if child.name == name:
                return child
    
    def push(self, node):
        self.childs.append(node)
        node.up = self
        return self

    def childs_source(self, tab=""):
        return "".join([x.source(tab) for x in self.childs])

    def source(self, tab=""):
        return "%s" %self.childs_source(tab)

    def childs_header(self, tab=""):
        return "".join([x.header(tab) for x in self.childs])

    def header(self, tab=""):
        return "%s" %self.childs_header(tab)

class File(Node):
    def __init__(self, name):
        Node.__init__(self, name, self.__class__)
        self.file_name = name
        self.ifndef = name[0]
        self.hincludes = []
        self.cincludes = ["%s%s.hpp" %name]
    
    def source(self, tab=""):
        incs = "\n".join("#include \"%s\"" %x for x in self.cincludes)
        
        return "".join([
            "%s\n" %incs,
            "%s" %self.childs_source(tab)
        ])

    def header(self, tab=""):
        incs = "\n".join("#include \"%s\"" %x for x in self.hincludes)
        name = self.ifndef.upper()
        return "".join([
            "#ifndef SLX_H_%s\n" %name,
            "#define SLX_H_%s\n" %name,
            "%s\n" %incs,
            "%s\n" %self.childs_header(tab),
            "#endif // SLX_H_%s\n" %name
        ])

class Package(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = "p_" + name
        self.hide = False
        self.super = None
    
    def source(self, tab=""):
        if self.hide:
            return ""
        
        self.cname = "p_" + self.name
        
        if self.name == "":
            return self.childs_source(tab)
        
        return "%snamespace %s {\n%s\n%s}\n" %(
            tab, self.cname, self.childs_source(tab + "\t"), tab)
    
    def header(self, tab=""):
        if self.hide:
            return ""
        
        self.cname = "p_" + self.name
        
        if self.name == "":
            return self.childs_header(tab)
        
        return "%snamespace %s {\n%s\n%s}\n" %(
            tab, self.cname, self.childs_header(tab + "\t"), tab)

class Hpp(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.line = ""

    def header(self, tab=""):
        return "%s%s\n" %(tab, self.line)

class Cpp(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.line = ""

    def source(self, tab=""):
        return "%s%s\n" %(tab, self.line)

class Line(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.line = ""
        self.head = False

    def source(self, tab=""):
        return "%s%s\n" %(tab, self.line)

    def header(self, tab=""):
        if self.head:
            return "%s%s\n" %(tab, self.line)
        
        return ""

class Expr(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.expr = None
        self.value = ""

    def source(self, tab=""):
        return "%s%s;\n" %(tab, self.get_expr(self.expr))

class Type(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.ref = None
        self.ptr = None
        self.array = []
    
    def source(self, tab=""):
        return self.cname
    
    def header(self, tab=""):
        return self.cname

class TypeDef(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name