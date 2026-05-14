tree = {
    "1": {
        "1.1": {
            "1.1.1": "a",
            "1.1.2": "b",
        },
        "1.2": {
            "1.2.1": "c",
            "1.2.2": "d",
        },
    },
    "2": {
        "2.1": {
            "2.1.1": "e",
            "2.1.2": "f",
        },
        "2.2": {
            "2.2.1": "g",
            "2.2.2": "h",
        },
    },
}

paths = [
    # [
    #     "1", "2", "1.1", "1.2", "2.1",
    #     "1.1.1", "1.1.2", "2.1.1"
    # ],
    [
        "2", "1", "2.2", "1.1", "1.2",
        "2.2.1", "1.2.2", "1.1.1"
    ],
    [
        "1", "1.2", "2", "2.1", "2.2",
        "1.2.1", "2.1.2", "2.2.2"
    ],
    [
        "2", "2.1", "1", "1.1", "1.2",
        "2.1.1", "1.1.2", "1.2.1"
    ],
    [
        "1", "2", "0.1", "0.2", "0.2",
        "1.1.1", "2.2.2", "1.2.2"
    ],
]

def get_by_path(tree, path):
    node = tree
    for key in path:
        node = node[key]
    return node


def find_path_in_tree(tree, items, path2elem = None):
    """
        Funkcja opowiada za odnalezienie poprawnej struktury która powoduje daną akcje
    """
    if path2elem is None:  path2elem = []

    fp =  path2elem.copy()
    for itm in items:
        if itm in tree:
            print("<<---", itm, "---", tree.get(itm.__class__))
            if isinstance(tree[itm], dict):
                path2elem = fp + [itm]
                path2elem  = find_path_in_tree(tree[itm], items, path2elem)
                if path2elem != None: break
            elif isinstance(tree.get(itm.__class__), dict):
                path2elem = fp + [itm]
                path2elem = find_path_in_tree( tree.get(itm.__class__), items, path2elem)
                if path2elem != None: break
            else:
                path2elem.append(itm)
                break
    else:
        return None
    return path2elem.copy()

def part_path_in_tree(tree, items, path2elem = None):
    """
        Funkcja odszukuje pierwszy elemnt pasujacy do drzewa i na jego podstawie buduje sierz
        pierwsza znaleziona ścieżka
    """
    if path2elem is None:  path2elem = []

    for itm in items:
        if itm in tree:
            print( ">---", itm, "---", tree.get(itm.__class__))
            if isinstance(tree[itm], dict):
                path2elem.append(itm)
                p2e  = path2elem.copy()
                path2elem = part_path_in_tree(tree[itm], items, path2elem)
                if path2elem == None:
                    return p2e
                break
            elif isinstance( tree.get(itm.__class__), dict):
                path2elem.append(itm.__class__)
                p2e = path2elem.copy()
                path2elem = part_path_in_tree( tree.get(itm.__class__), items, path2elem)
                if path2elem == None:
                    return p2e
                break
            else:
                path2elem.append(itm)
                break
    else:
        return None
    return path2elem


for p in paths:
    print("\n==>",p)

    result = part_path_in_tree(tree, p)
    print(result)

    # if result != None:
    #     print( get_by_path(tree, result) )
    #
    # result = find_path_in_tree(tree,p)
    # print(result)
    #
    # if result != None:
    #     print( get_by_path(tree, result) )
    #
    # result = None