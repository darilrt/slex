import argparse
import copy
import sxg
import sys
import IR
import os

class Sxc:
    def __init__(self, grm_path, file_path, dir, out, first=False):
        self.grm = sxg.Grammar()
        self.grm_path = grm_path
        self.load_grammar_defs(grm_path)
        self.dir = dir
        self.odir = out
        
        self.irs = IR.Scanner(self.grm, file_path, first=first)
        self.first = first
        self.add_defs()
        self.next_as = ''
        self.files = []

    def source(self):
        return self.irs.node.source()

    def header(self):
        return self.irs.node.header()

    def generate_ir(self):
        self.irs.generate()
        
    def load_grammar_defs(self, file_path):
        _lines = []
        with file(file_path, "r") as f:
            _lines = f.readlines()

        lines = []
        acc = ""
        pos = 0
        for line in _lines:
            pos += 1
            stp = line.strip()

            if stp[-1:] == "\\":
                acc += stp[:-1]

            elif acc != "":
                lines.append([acc + stp, pos])
                acc = ""
    
            elif stp != "":
                lines.append([stp, pos])
            
        for line in lines:
            self.grm.load_def(*line)

    def add_defs(self):
        @self.irs.add("use_stmt")
        def func(irs, data, ident):
            tmp = data['name'].copy()
            lst = [tmp] + tmp.pop('list')
            
            irs.compiled_files.append("/".join(x['name'] for x in lst))
            
            folder = ""
            for n in lst:
                folder += "/" + n['name']
            
            folder += "/"
            
            list_files = os.listdir(self.dir + folder)
            slx_files = []
            
            for f in list_files:
                if os.path.splitext(f)[1] == '.slx':
                    slx_files.append(f)
            
            for slxf in slx_files:
                file_path = self.dir + folder + slxf
                
                sxc = Sxc(
                    self.grm_path,
                    file_path,
                    self.dir,
                    self.odir
                )
                
                sxc.generate_ir()
                irs.node.hincludes += sxc.irs.node.hincludes
                irs.node.cincludes += sxc.irs.node.cincludes
                irs.node.cincludes.remove("%s%s.hpp" %sxc.irs.node.name)
                irs.node.hincludes = list(dict.fromkeys(irs.node.hincludes))
                
                n = "".join(sxc.irs.node.name)
                
                nod = irs.node
                pkg = sxc.irs.node
                for n in lst:
                    pkg = pkg.find(IR.Package, n['name'])
                    t = nod.find(IR.Package, n['name'])
                    
                    if not t:
                        _node = IR.Package()
                        _node.name = pkg.name
                        _node.cname = pkg.cname
                        _node.up = nod
                        
                        nod.childs = [_node] + nod.childs
                        nod = _node
                    
                    else:
                        nod = t
                
                nod.childs = pkg.childs + nod.childs
                
                pkg = copy.copy(pkg)
                pkg.hide = True
                
                if data['all'] != None:
                    irs.packages.append(pkg)
                
                elif data['as']:
                    print data['as']
            
            return IR.Null()
        
        @self.irs.add("package_stmt")
        def func(irs, data, ident):
            tmp = data['name'].copy()
            lst = [tmp] + tmp.pop('list')
            
            c = irs.self_package
            irs._stack_current = []
            irs.current = None
            
            pack = IR.Node()
            last = None
            for p in lst:
                n = IR.Package()
                n.name = p['name']
                
                if last:
                    n.super = last
                    last.push(n)
                
                else:
                    n.super = pack
                    pack.push(n)
                
                last = n
                irs.set(n)
            
            irs.node.childs.remove(irs.node.find(IR.Package, ""))
            irs.node.push(pack.childs[0])
            
            irs.self_package = last
            irs.node.childs = c.childs + irs.node.childs
            
            irs.set(last)
            irs.childs_by_ident(last, ident)
            irs.unset()
            
            return IR.Null()
        
        @self.irs.add("link_stmt")
        def func(irs, data, ident):
            if data['line'] not in irs.libs:
                irs.libs.append(data['line'])
            return IR.Null()
        
        @self.irs.add("include_stmt")
        def func(irs, data, ident):
            if data['line'] not in irs.node.hincludes:
                irs.node.hincludes.append(data['line'])
            
            return IR.Null()
        
        @self.irs.add("cpp_stmt")
        def func(irs, data, ident):
            node = IR.Cpp()
            node.line = data['line']
            return node
        
        @self.irs.add("hpp_stmt")
        def func(irs, data, ident):
            node = IR.Hpp()
            node.line = data['line']
            return node
        
        @self.irs.add("return_stmt")
        def func(irs, data, ident):
            node = IR.Return()
            node.irs = irs
            
            if data['expr'] != None:
                node.expr = data['expr']
            
            return node
        
        # SWITCH
        
        @self.irs.add("switch_stmt")
        def func(irs, data, ident):
            node = IR.Switch()
            node.irs = irs
            
            node.condition = data['expr']
            node.ccondition = irs.get_expr(data['expr'])
            
            irs.childs_by_ident(node, ident)
            
            return node
        
        @self.irs.add("case_stmt")
        def func(irs, data, ident):
            node = IR.SwitchCase()
            node.irs = irs
            
            node.condition = data['expr']
            node.ccondition = irs.get_expr(data['expr'])
            
            irs.childs_by_ident(node, ident)
            
            return node
        
        @self.irs.add("default_stmt")
        def func(irs, data, ident):
            node = IR.SwitchDefault()
            
            irs.childs_by_ident(node, ident)
            
            return node
        
        # ======
        
        @self.irs.add("deco")
        def func(irs, data, ident):
            if data['cmd'] == 'static':
                self.next_as = 'static'
            
            elif data['cmd'] == 'virtual':
                self.next_as = 'virtual'
                
            elif data['cmd'] == 'main':
                self.next_as = 'main'
                
            elif data['cmd'] == 'header':
                self.next_as = 'header'
            
            return IR.Null()
        
        @self.irs.add("while_stmt")
        def func(irs, data, ident):
            node = IR.While()
            node.irs = irs
            
            node.condition = data['expr']
            node.ccondition = irs.get_expr(data['expr'])
            
            irs.set(node)
            irs.childs_by_ident(node, ident)
            irs.unset()
            
            return node
        
        @self.irs.add("if_stmt")
        def func(irs, data, ident):
            node = IR.If()
            node.irs = irs
            
            node.condition = data['expr']
            node.ccondition = irs.get_expr(data['expr'])
            
            irs.set(node)
            irs.childs_by_ident(node, ident)
            irs.unset()
            
            return node
        
        @self.irs.add("elif_stmt")
        def func(irs, data, ident):
            node = IR.Elif()
            node.irs = irs
            
            node.condition = data['expr']
            node.ccondition = irs.get_expr(data['expr'])
            
            irs.childs_by_ident(node, ident)
            
            return node
        
        @self.irs.add("else_stmt")
        def func(irs, data, ident):
            node = IR.Else()
            
            irs.childs_by_ident(node, ident)
            
            return node
        
        @self.irs.add("class_define")
        def func(irs, data, ident):
            node = IR.Class()
            node.irs = irs
            node.name = data['name']
            node.cname = "c" + data['name']
            irs.current.push(node)
            
            if self.next_as == 'header':
                node.head = True
                node.hide = True
                self.next_as = ""
            
            if data['inher']:
                inh = data['inher'].copy()
                node.inher = [inh] + inh.pop('list')
            
            if data['template'] != None:
                node.template = [data['template']] + data['template'].pop('list')
                
                for tmp in node.template:
                    n = IR.TypeDef(tmp['name'])
                    n.irs = irs
                    n.set_current_context()
                    n.cname = tmp['name']
                    n.all_props = True
                    node.push(n)
            
            irs.set(node)
            irs.childs_by_ident(node, ident)
            irs.unset()
            return IR.Null()
            
        @self.irs.add("func_define")
        def func(irs, data, ident):
            node = IR.Function()
            node.name = data['name']
            
            if self.next_as == 'static':
                node.static = True
            
            elif self.next_as == 'virtual':
                node.virtual = True
            
            self.next_as = ''
            
            if data['template'] != None:
                node.template = [data['template']] + data['template'].pop('list')
                
                for tmp in node.template:
                    n = IR.TypeDef(tmp['name'])
                    n.irs = irs
                    n.cname = tmp['name']
                    n.all_props = True
                    node.push(n)
            
            parent = irs.current
            irs.set(node)
            irs.check_type(data['type'])
            node.type = irs.get_type(data['type'])
            
            if parent.__class__ == IR.Class:
                n = IR.Variable('self')
                node.push(n)
                n.hide = True
                n.type = ('this', parent, {'ref': None, 'ptr': [{'ptr': '*'}]})
                n.cname = 'this'
                
                if data['type'] != None and node.name == parent.name:
                    irs.fatal("TypeError", "invalid constructor return type")
            
            if data['args'] != None:
                data['args'].pop('__name__')
                arg_lst = [data['args']['var']] + [x['var'] for x in data['args'].pop('list')]
                
                for arg in arg_lst:
                    n = IR.Variable()
                    n.hide = True
                    n.irs = irs
                    n.set_current_context()
                    n.name = arg['name']
                    
                    irs.check_type(arg['type'])
                    n.type = irs.get_type(arg['type'])
                    
                    n.indexs = [e['expr'] for e in arg['array']]
                    node.push(n)
                    node.args.append(n)
            
            irs.childs_by_ident(node, ident)
            irs.unset()
            
            node.source()
            return node
        
        @self.irs.add("var_define")
        def func(irs, data, ident):
            data.pop('__name__')
            
            dtype = data.pop('type')
            
            lst = [data] + data.pop('list')
            
            for var in lst:
                node = IR.Variable()
                node.irs = irs
                node.set_current_context()
                
                if irs.current.exists(var['name']):
                    irs.multiple_definition(var['name'])
                
                elif irs.node.exists(var['name']):
                    irs.multiple_definition(var['name'])
                
                if var['assign'] != None and var['assign']['expr'] == None:
                    irs.invalid_syntax()
                
                elif var['assign'] != None:
                    node.assign = var['assign']['expr']
                    irs.get_expr(var['assign']['expr'])
                    
                irs.check_type(dtype)
                    
                node.name = var['name']
                node.type = irs.get_type(dtype.copy())
                node.indexs = [e['expr'] for e in var['array']]
                
                for ex in node.indexs:
                    irs.get_expr(ex)
                
                irs.current.push(node)
                
            return IR.Null()
        
        @self.irs.add("var_assign")
        def func(irs, data, ident):
            
            names = [{'name': data['name']}] + data['nlist']
            values = [{'expr': data['expr']}] + data['elist']
            
            if len(names) != len(values):
                irs.invalid_syntax()
            
            for i in xrange(len(names)):
                node = IR.Assign()
                node.irs = irs
                node.set_current_context()
                
                node.name = names[i]['name']
                node.cname = irs.get_dotted(names[i]['name'])
                
                node.expr = values[i]['expr']
                node.value = irs.get_expr(values[i]['expr'])
                
                irs.current.push(node)
                
            return IR.Null()
        
        @self.irs.add("expr")
        def func(irs, data, ident):
            node = IR.Expr()
            
            if data['expr'] != None:
                irs.get_expr(data.copy()['expr'])
                node.expr = data.copy()['expr']
            
            return node

def main():
    grm_file_path = "%s/grammar" %os.path.dirname(sys.argv[0])

    parser = argparse.ArgumentParser(description='Slex transpilator.')
    parser.add_argument('file', metavar='file', type=argparse.FileType('r'), nargs=1,
                       help='file to compile')
    
    parser.add_argument('-o', '--output', help='output folder')
    
    args = parser.parse_args()
    
    path = os.path.abspath(args.file[0].name)
    name = os.path.basename(path)
    args.file[0].close()
    
    out_dir = ""
    if args.output != None:
        if os.path.isdir(args.output):
            out_dir = os.path.abspath(args.output)
        
        else:
            print "usage: sxc.py [-h] [-o OUTPUT] file"
            print "sxc.py: error: argument -o/--output: is not a directory"
            exit()
    
    if out_dir == "":
        out_dir = os.path.dirname(path)
    
    sxc = Sxc(grm_file_path, path, os.path.dirname(path), out_dir, first=True)
    sxc.generate_ir()
    
    files = []
    libs = ["-lstdc++"]
    
    files.append("%s/%s.cpp" %(out_dir, name))

    cfile = file("%s/%s.cpp" %(out_dir, name), 'w+')
    cfile.write(sxc.irs.node.source())
    cfile.close()

    hfile = file("%s/%s.hpp" %(out_dir, name), 'w+')
    hfile.write(sxc.irs.node.header())
    hfile.close()
    
    os.system("gcc " + " ".join(files) + " -o %s\%s.exe %s" %(
        out_dir,
        sxc.irs.node.name[0],
        " ".join(libs)
    ))
    
if __name__ == "__main__":
    main()