from sys import argv
from pyverilog.vparser import parser
from pyverilog.vparser import ast as _ast

def delete_multiline_comment(code:str) -> str:
    first = code.find("/*")
    last = code.find("*/")
    return code[:first] + code[last+2:]

def report_object(module):
    print(type(module))
    print(module)
    print(module.lineno)
    print(dir(module))

def IGNORE():
    print("", end="")

# TODO: Handle keywords I use in AST
# Search in code for `KEYWORDS: `

def _forward_traverse_generic_block(block):
    return traverse_generic_block(block)

def _forward_traverse_condition(condition) -> list:
    return traverse_condition(condition)

def traverse_block(block) -> list:
    block_tree = []
    for k in block.children():
        block_tree.extend(traverse_generic_block(k))
    return block_tree

def traverse_lrvalue(value) -> list:
    """Extension (not child)"""
    if type(value) == _ast.Identifier:
        return [value.name]
    elif type(value.var) == _ast.Identifier:
        return [value.var.name]
    elif type(value.var) in [_ast.IntConst, _ast.Partselect]:
        return []
    elif type(value.var) in [_ast.Plus, _ast.Minus, _ast.LConcat]:
        return _forward_traverse_condition(value.var)
    elif type(value.var) == _ast.Pointer:
        return traverse_lrvalue(value.var)
    print(type(value.var))
    report_object(value.var)
    assert False

def traverse_blocking_substitution(blocking_substitution) -> list:
    subs_tree = []
    subs_tree.extend(traverse_lrvalue(blocking_substitution.left))
    subs_tree.extend(traverse_lrvalue(blocking_substitution.right))
    return subs_tree

tree_cond = [_ast.Lor, _ast.Eq, _ast.NotEq, _ast.LessThan, _ast.GreaterEq, _ast.LessEq, 
             _ast.GreaterThan, _ast.Plus, _ast.Land, _ast.Minus, _ast.LConcat]
def traverse_lor(lor) -> list:
    out = []
    if type(lor.left) in tree_cond:
        out.append(traverse_lor(lor.left))
    else:
        out.extend(_forward_traverse_condition(lor.left))
    if type(lor.right) == tree_cond:
        out.append(traverse_lor(lor.right))
    else:
        out.extend(_forward_traverse_condition(lor.right))
    return out

def traverse_condition(condition) -> list:
    """The returned list must be used for extension, not as a child"""
    if type(condition) == _ast.Identifier:
        return [condition.name]
    elif type(condition) == tuple:
        out = []
        for item in condition:
            out.extend(traverse_condition(item))
        return out
    elif type(condition) == _ast.IntConst:
        return []
    elif type(condition) in tree_cond:
        return traverse_lor(condition)
    elif condition is None:
        return []
    print(type(condition))
    report_object(condition)

def traverse_if_statement(if_statement) -> list:
    if_tree = []
    if_tree.extend(traverse_condition(if_statement.cond))
    if_tree.extend(_forward_traverse_generic_block(if_statement.false_statement))
    if_tree.extend(_forward_traverse_generic_block(if_statement.true_statement))
    return if_tree

def traverse_case(case) -> list:
    case_tree = []
    case_tree.extend(traverse_condition(case.cond))
    case_tree.extend(_forward_traverse_generic_block(case.statement))
    return case_tree

def traverse_case_statement(case_statement) -> list:
    case_statement_tree = []
    case_statement_tree.extend(traverse_lrvalue(case_statement.comp))
    for case in case_statement.caselist:
        case_statement_tree.extend(traverse_case(case))
    return case_statement_tree

def traverse_always(always) -> list:
    always_tree = []
    for sens in always.sens_list.children():
        #report_object(sens)
        for signal in sens.children():
            always_tree.append(signal.name)
    for k2 in always.statement.children():
        always_tree.extend(traverse_generic_block(k2))
    return always_tree

def traverse_port_list(port_list) -> list:
    port_tree = []
    for port in port_list.ports:
        port_tree.append(port.name)
    return port_tree

def traverse_decl(decl) -> list:
    decl_tree = []
    for k in decl.children():
        # We have already added all ports as children, so we won't consider them again
        if type(k) not in [_ast.Input, _ast.Output, _ast.Inout]:
            # Make sure we cover all types
            if type(k) in [_ast.Parameter, _ast.Reg, _ast.Wire]: 
                decl_tree.append(k.name)
            else:
                report_object(k)
                print(130)
                assert False
    return decl_tree

def traverse_generic_block(generic):
    if type(generic) == _ast.IfStatement:
        return traverse_if_statement(generic)
    elif type(generic) == _ast.Block:
        return traverse_block(generic)
    elif type(generic) in [_ast.BlockingSubstitution, _ast.Assign, _ast.NonblockingSubstitution]:
        return traverse_blocking_substitution(generic)
    elif (type(generic) == _ast.Lvalue) or (type(generic) == _ast.Rvalue):
        return traverse_lrvalue(generic)
    elif (type(generic) in [_ast.CaseStatement, _ast.CasexStatement, _ast.CasezStatement, _ast.UniqueCaseStatement]):
        return traverse_case_statement(generic)
    elif type(generic) == _ast.Lor:
        return traverse_lor
    elif generic is None:
        return []       # TODO: Is this correct?
    elif type(generic) == _ast.SingleStatement:
        return traverse_block(generic)
    elif type(generic) == _ast.SystemCall:
        return []
    elif type(generic) == _ast.Always:
        return traverse_always(generic)
    elif type(generic) == _ast.Portlist:
        return traverse_port_list(generic)
    elif type(generic) == _ast.Paramlist:
        return []
    elif type(generic) == _ast.Decl:
        return traverse_decl(generic)
    elif type(generic) == _ast.Partselect:
        return []           # TODO: Check
    report_object(generic)
    assert 0

def traverse_ast(ast):
    output_tree = {}
    for modules in ast.children():
        for module in modules.children():
            module_tree = []
            modulename = module.name
            for k in module.children():
                module_tree.extend(traverse_generic_block(k))
            output_tree[modulename] = module_tree
    return output_tree

def ast_from_file(path:str) -> dict:
    with open(path, "r") as fin:
        ast, directives = parser.parse(fin)
    return traverse_ast(ast)

if __name__ == "__main__":
    if len(argv) != 3:
        print("Usage: " + argv[0] + " <input.v> <output.v>")
        print("Remove comments and make sure each line contains exactly one statement. ")
        exit(1)
    
    srcpath = argv[1]
    dstpath = argv[2]

    srcfile = open(srcpath, "r")
    dstfile = open(dstpath, "w")

    ast, directives = parser.parse(srcfile)
    
    tree = traverse_ast(ast)
    print(tree)

    srcfile.close()
    dstfile.close()