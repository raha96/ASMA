from ast_gen import ast_from_file
from sys import argv
from queue import Queue

def list_names(tree) -> set:
    names = set()
    if type(tree) is list:
        for node in tree:
            names = names.union(list_names(node))
    elif type(tree) is dict:
        for key in tree:
            names.add(key)
            names = names.union(list_names(tree[key]))
    elif type(tree) is str:
        names.add(tree)
    else:
        print(type(tree))
        print(tree)
        assert False
    return names

def create_name_map(tree:list) -> dict:
    names = set(list_names(tree))
    mapping = {}
    for name in names:
        mapping[name] = len(mapping) + 1
    return mapping

def map_tree(tree, name_map:dict) -> list:
    out = []
    if type(tree) == list:
        for node in tree:
            out.extend(map_tree(node, name_map))
    elif type(tree) == dict:
        for key in tree:
            out.append(name_map[key])
            out.extend(map_tree(tree[key], name_map))
    elif type(tree) == str:
        out.append(name_map[tree])
    else:
        assert False
    return out

def map_all_trees_dict(ast:dict) -> dict:
    out = {}
    for ast_name in ast:
        named_tree = ast[ast_name]
        mapping = create_name_map(named_tree)
        out[ast_name] = map_tree(named_tree, mapping)
    return out

def map_all_trees_list(ast:list) -> dict:
    mapping = create_name_map(ast)
    return map_tree(ast, mapping)

def _feature_vector(subtree:list) -> tuple:
    nodes = []
    subtrees = Queue()
    for node in subtree:
        if type(node) == list:
            subtrees.put(node)
        else:
            assert type(node) == int
            nodes.append(node)
    return subtrees, nodes

def create_feature_vector(tree:list) -> list:
    subtrees, out = _feature_vector(tree)
    while subtrees.qsize():
        current = subtrees.get()
        new_subtrees, new_nodes = _feature_vector(current)
        while new_subtrees.qsize():
            subtrees.put(new_subtrees.get())
        out.extend(new_nodes)
    return out

def create_root_vectors(ast:dict) -> dict:
    all_mapped = map_all_trees_dict(ast)
    out = {}
    for ast_name in all_mapped:
        tree = all_mapped[ast_name]
        out[ast_name] = create_feature_vector(tree)
    return out

def extract_all_subtrees(tree:list) -> list:
    assert type(tree) == list
    out = [tree]
    for node in tree:
        if type(node) == list:
            out.extend(extract_all_subtrees(node))
    return out

def create_all_vectors_dict(ast:dict) -> list:
    all_mapped = map_all_trees_dict(ast)
    out = []
    for ast_name in all_mapped:
        subtrees = extract_all_subtrees(all_mapped[ast_name])
        for subtree in subtrees:
            out.append(create_feature_vector(subtree))
    return out

def create_all_vectors_list(ast:list) -> list:
    all_mapped = map_all_trees_list(ast)
    out = []
    subtrees = extract_all_subtrees(all_mapped)
    for subtree in subtrees:
        out.append(create_feature_vector(subtree))
    return out

if __name__ == "__main__":
    ast = ast_from_file(argv[1])
    features = create_all_vectors_dict(ast)
    print(features)