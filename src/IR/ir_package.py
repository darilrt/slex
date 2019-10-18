from ir_node import Node
import IR

class Include(Node): # unused
    def __init__(self, name=""):
        Node.__init__(self, name, self.__class__)
        self.cname = name
        self.condition = []
    
    def source(self, tab=""):
        return "%sif (%s) {\n%s%s}\n" %(
            tab, self.ccondition,
            self.childs_source(tab + "\t"), tab
        )
