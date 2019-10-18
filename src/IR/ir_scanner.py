from sxg import Operand
import IR
import os

class Scanner:
    def __init__(self, grm, file_path):
        self.file_path = file_path
        
        self.lines = []
        self.pos = -1
        
        with file(file_path, "r") as f:
            self.lines = f.readlines()
        
        self.grm = grm

        self.node = IR.File(os.path.splitext(os.path.basename(file_path)))
        self._stack_current = [self.node]
        self.current = None
        self.packages = []
        self.self_package = None
        self.as_header = False

        self.identation = ""

        self._funcs = []
        self._funcs_for_head = []
        self._last_name = ""
        
        self._init_primitives()
        
        self.op_to_c = {
            "and": "&&",
            "or": "||",
            "not": "!",
            "is": "=="
        }
    
    def _init_primitives(self):
        self._push_primitive('void', 'void')
        self._push_primitive('bool', 'bool')
        self._push_primitive('i8'  , 'char')
        self._push_primitive('i16' , 'short')
        self._push_primitive('i32' , 'int')
        self._push_primitive('i64' , 'long long int')
        self._push_primitive('u8' , 'unsigned char')
        self._push_primitive('u16', 'unsigned short')
        self._push_primitive('u32', 'unsigned int')
        self._push_primitive('u64', 'unsigned long long int')
        self._push_primitive('f64' , 'float')
        self._push_primitive('f64' , 'double')
        
        self._push_var('true'  , 'true')
        self._push_var('false' , 'false')
        self._push_var('and'  , '&&')
        self._push_var('or' , '||')
        self._push_var('not' , '!')
        self._push_var('is' , '==')
    
    def _push_primitive(self, name, cname):
        node = IR.TypeDef(name)
        node.cname = cname
        self.node.push(node)
    
    def _push_var(self, name, cname):
        node = IR.Variable(name)
        node.hide = True
        node.cname = cname
        node.type = (cname, 0, 0)
        self.node.push(node)
    
    def fatal(self, type, message):
        print "\nFile \"%s\" line %i" %(self.file_path, self.pos + 1)
        
        if self.pos < len(self.lines):
            print "    %s\n" %self.lines[self.pos].strip()
        
        print "%s: %s" %(type, message)
        exit()
        
    def log(self, message):
        print "\nFile \"%s\" line %i" %(self.file_path, self.pos + 1)
        print "    %s\n" %self.lines[self.pos].strip()
        print "Log: %s" %(message)
        
    def invalid_syntax(self):
        self.fatal("SyntaxError", "invalid syntax")
        
    def multiple_definition(self, name):
        self.fatal("Error", "multiple definition of \"%s\"" %name)
    
    def set(self, node):
        self.current = node
        self._stack_current.append(self.current)

    def unset(self):
        self.current = self._stack_current.pop()
        self.current = self._stack_current[-1]

    def next_line(self):
        self.pos += 1

        if self.pos < len(self.lines):
            return self.lines[self.pos]

        return -1
    
    def _add_func(self, func):
        self._funcs.append({
            "def": self._last_name,
            "callback": func
        })

        if self._last_head:
            self._funcs_for_head.append({
                "def": self._last_name,
                "callback": func
            })

    def add(self, def_name, header=False):
        self._last_name = def_name
        self._last_head = header
        return self._add_func
    
    def _ident_level(self, line):
        if self.identation == "":
            c = len(line) - len(line.lstrip())
            self.identation = line[:c] if line[:c] != "\n" else ""
        
        if self.identation == "":
            return 0
        
        count = 0
        l = len(self.identation)
        line_ = line
        
        while len(line_) > l:
            d = line_[:l]
            if d == self.identation:
                count += 1

            else:
                break

            line_ = line_[l:]
        
        return count
    
    def _next(self, cident=0):
        line = self.next_line()

        if line == -1:
            return -1

        self.grm.set_line(line)
        
        if line.strip() == "" or len(self.grm.list) == 0:
            return -2

        ident = self._ident_level(line)
        
        if ident < cident:
            return -1

        error = True
        node = IR.Node()
        for func in self._funcs:
            data = {}
            
            if self.grm.parse(func['def'], data):
                cdata = data.copy()
                node = func['callback'](self, cdata, cident)
                
                if node.__class__ != IR.Null:
                    node.irs = self
                    node.set_current_context()
                
                error = False
                break
        
        if error:
            self.invalid_syntax()
        
        return node
    
    def check_type(self, vtype):
        self.get_type(vtype)
    
    def get_expr(self, list):
        if list == None:
            return ""
        
        out = []
        
        for _op in list:
            op = Operand(_op.sign, _op.type, _op.data)
            
            if type(_op.data) == dict:
                op.data = _op.data.copy()
            
            if op.type == Operand.NUMBER:
                out.append(op.data['val'])
            
            elif op.type == Operand.STRING:
                out.append("\"%s\"" %op.data['val'])
            
            elif op.type == Operand.VARIABLE:
                out.append(self.get_dotted(op.data))
            
            elif op.type == Operand.FUNCTION:
                args = []
                temp = ""
                
                if op.data['template']:
                    tmp = op.data['template'].copy()
                    lst = [tmp] + tmp.pop("list")
                    
                    temp = "<%s>" %", ".join([
                        str(self.get_type(x["type"])[0])
                        for x in lst
                    ])
                
                if op.data['args']:
                    args_list = [op.data['args']] + op.data['args'].copy().pop('list')
                    
                    for arg in args_list:
                        if arg['expr']:
                            args.append(self.get_expr(arg['expr']))
                
                args = ", ".join(args)
                name = self.get_dotted(op.data['name'])
                
                out.append("%s(%s)" %(name + temp, args))
            
            elif op.type == Operand.PARENT:
                out.append("(%s)" %self.get_expr(op.data))
            
            elif op.type == Operand.OPERATION:
                out.append(op.data)
            
            elif op.type == Operand.INSTANCING:
                if op.data['__name__'] == "dotted_name":
                    info = self.get_dotted(op.data)
                    size = []
                    
                    if op.data['arr'] != None:
                        for arr in op.data['arr']:
                            if arr['def']['expr'] != None:
                                size.append("(%s)" %self.get_expr(arr['def']['expr']['expr']))
                            
                            else:
                                print "Invalid size"
                            
                    
                    out.append("malloc(sizeof(%s) * %s)" %(info[0], " * ".join(size)))
                    
                elif op.data['__name__'] == 'func_call':
                    info = self.get_dotted(op.data['name'])
                    
                    if info[1] != 'class':
                        print "Can't instance \"%s\" (\"%s\")" %(info[1], info[0])
                    
                    else:
                        out.append("new%s()" %(info[0]))
                
            else:
                out += str(op)
        
        return " ".join(out)
    
    def get_type(self, vtype):
        if vtype == None:
            return ("void", None)
        
        def check_next_types(list):
            for dtype in list:
                print dtype
        
        name = ""
        dname = vtype['name']
        
        r = self.find_type_in(self.node, vtype)
        if r[0]: return r[1], r[2], vtype
        
        for i in xrange(1, len(self._stack_current) + 1):
            p = self._stack_current[len(self._stack_current)-i]
            
            r = self.find_type_in(p, vtype)
            if r[0]: return r[1], r[2], vtype
        
        for p in self.packages:
            r = self.find_type_in(p, vtype)
            if r[0]: return r[1], r[2], vtype
        
        self.fatal("TypeError", "")
    
    def find_type_in(self, node, vtype):
        types = [IR.TypeDef, IR.Class]
        
        for typ in types:
            t = node.find(typ, vtype['name']['name'])
            if t:
                if len(vtype['name']['list']) > 0:
                    self.fatal("Error", "expected unqualified-id before \".\" token")
                    
                return 1, self._get_type_fmt(vtype) %t.cname, t, vtype
        
        return 0, None, None
   
    def _get_type_fmt(self, vtype):
        fmt = ""
        if vtype['ref'] != None:
            fmt += " &"
        
        for p in vtype['ptr']:
            fmt = "*" + fmt
        
        if vtype['template']:
            tmp = vtype['template']
            print vtype['template']
            lst = [{'name': tmp['name']}] + tmp['list']
            lst = ", ".join([self.get_type(x['name'])[0] for x in lst])
            fmt = "<%s>" %(lst) + fmt
            
        return "%%s%s" %fmt
    
    def _get_dottend_one(self, ele, ctx):
        name = ""
        type = None
        
        if ctx:
            if ctx.all_props:
                t = ctx.find(IR.Variable, ele['name'])
                type = IR.Variable()
                type.name = ele['name']
                type.cname = "p_" + ele['name']
                type.type = ("", IR.Class.accept_props(), {'ptr': None, 'ref': None})
                
                if t:
                    type.type[2] = t.type[2]
                
                return type.cname, type
            
            t = ctx.find(IR.Variable, ele['name'])
            if t:
                type = t
                name = t.cname
            
            t = ctx.find(IR.Function, ele['name'])
            if t:
                type = t
                name = t.cname
        
        else:
            for m in self._stack_current:
                t = m.find(IR.Variable, ele['name'])
                if t:
                    type = t
                    name = t.cname
                    break
                
                t = m.find(IR.Function, ele['name'])
                if t:
                    type = t
                    name = t.cname
                    break
            
            if type != None:
                return name, type
            
            p = None
            for m in self.packages:
                p = m
                t = m.find(IR.Variable, ele['name'])
                if t:
                    type = t
                    name = t.cname
                    break
                
                t = m.find(IR.Function, ele['name'])
                if t:
                    type = t
                    name = t.cname
                    break
            
            pkg = ""
            if type != None and p != None:
                while p != None and p.__class__ == IR.Package:
                    pkg = "p_%s::" %p.name + pkg
                    p = p.super
                
                name = pkg + name
                return name, type
            
            t = self.node.find(IR.Package, ele['name'])
            if t:
                t.type = (1, 1, 1)
                type = t
                name = "p_" + type.name
                
                p = t.super
                while p != None and p.__class__ == IR.Package:
                    name = "p_%s::" %p.name + name
                    p = p.super
        
        if ele.has_key('array'):
            for e in ele['array']:
                name += "[%s]" %(self.get_expr(e['expr']))
        
        if name == "":
            self.fatal("NameError", "name \"%s\" is not defined" %ele['name'])
        
        return name, type
    
    def get_dotted(self, _dict):
        dict = _dict.copy()
        if dict.has_key('__name__'): dict.pop('__name__')
        
        lst = [dict] + dict.pop('list')
        
        cname = ""
        last = None
        conn = ""
        for ele in lst:
            ret = self._get_dottend_one(ele, last)
            cname += conn + ret[0]
            
            conn = ""
            
            if ret[1] == None or ret[1].type[1] == 0:
                if len(lst) > 1:
                    if last:
                        self.fatal('Error', '\"%s\" is not property of \"%s\"' %(ele['name'], last.name))
                    
                    else:
                        self.fatal('Error', '\"%s\" have not property' %(ele['name']))
                    
                else:
                    break
            
            last = ret[1].type[1]
            
            if last == 1:
                last = ret[1]
            
            if ret[1].__class__ == IR.Package:
                conn = "::"
            
            elif ret[1].__class__ == IR.Class:
                conn = "::"
                
            elif ret[1].__class__ == IR.Variable:
                if ret[1].type[1] != 0:
                    if ret[1].type[1].all_props:
                        conn = "."
                        
                    if ret[1].type[1].__class__ == IR.Class:
                        conn = "."
                        
                    if ret[1].type[2]['ref']:
                        conn = "."
                    
                    elif ret[1].type[2]['ptr']:
                        conn = "->"
                
                else:
                    pass
    
        return cname
    
    def childs_by_ident(self, parent, cident):
        cident += 1
        node = self._next(cident)

        while node != -1:
            if node != -2:
                node.irs = self
                if node.__class__ != IR.Null:
                    parent.push(node)

            node = self._next(cident)

        self.pos -= 1
    
    def read_header(self, path):
        irs = Scanner(path)
    
    def generate(self):
        if len(self.packages) == 0:
            pkg = IR.Package("")
            self.node.push(pkg)
            self.packages.append(pkg)
            self.set(pkg)
            self.self_package = pkg
        
        else:
            pkg = self.packages[0]
        
        node = self._next()

        while node != -1:
            if node != -2:
                node.irs = self
                
                if node.__class__ != IR.Null:
                    self.self_package.push(node)

            node = self._next()