from ir_node import Node
import IR

class Class(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.inher = None
        self.hide = False
        self.head = False
        self.template = []
        
    @staticmethod
    def accept_props():
        t = Class()
        t.all_props = True
        return t
    
    def push(self, child):
        if child.__class__ == IR.Function:
            child.parent = self
            
            if self.head:
                child.cname = child.name
            
            # check if contructor
            if child.name == self.name:
                child.cname = 'c%s' %self.name
                child.constructor = True
                child.type = ["", None]
        
        elif child.__class__ == IR.Variable:
            child.parent = self
            
            child.cname = 'p_%s' %child.name
            
            if self.head:
                child.cname = child.name
        
        self.childs.append(child)
    
    def source(self, tab=""):
        if self.hide:
            return ""
    
        if self.cname == "":
            self.cname = "c%s" %self.name
        
        src = ""
        for child in self.childs:
            if child.__class__ == IR.Function:
                src += child.source()
        
        return src
    
    def header(self, tab=""):
        if self.hide:
            return ""
        
        if self.cname == "":
            self.cname = "c%s" %self.name
        
        inh = ""
        tmp = ""
        
        if len(self.template) > 0:
            tmp = ", ".join(["typename %s" %e['name'] for e in self.template])
            tmp = "%stemplate<%s>\n" %(tab, tmp)
        
        if self.inher != None:
            inh = ": "
            lst = []
            for c in self.inher:
                c['ref'] = None
                c['ptr'] = []
                c['name'] = c.pop('class')
                
                lst.append("public %s" %self.get_type(c.copy())[0])
            
            inh += ", ".join(lst)
            
        src = ""
        for child in self.childs:
            if child.__class__ == IR.Variable:
                src += child.source(tab + "\t")
            
            elif child.__class__ == IR.Function:
                src += child.header(tab + "\t")
        
        return "\n%s%sclass %s%s {\n%spublic:\n%s%s};\n" %(
            tmp, tab, self.cname, inh, tab, src, tab
        )

class Struct(Node):
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)