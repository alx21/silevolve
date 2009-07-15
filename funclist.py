# Produce all functions that we want the AI to have access to

def add(x,y):
    """add"""
    return resolve(x) + resolve(y)

def sub(x,y):
    """sub"""
    return resolve(x) - resolve(y)

def mul(x,y):
    """mul"""
    return resolve(x)*resolve(y)

def div(x,y):
    """div"""
    y = resolve(y)
    if y == 0: return 0 # that clears that up!
    return int(resolve(x)//y)

def power(x,y):
    """pow"""
    x = resolve(x)
    if x == 0: return 0
    return int(x**resolve(y))

def intInsert(): return # will never actually be called, special case handled
                        # by the resolve funcion.

def dataInsert(x):
    """data"""
    y = resolve(x)
    if y > 0 and y < len(data): return data[y]
    return 0 # should this be something less relevant?

def ifStatement(x,y,z):
    """if"""
    if resolve(x) > 0: return resolve(y)
    return resolve(z)
    
def treeParser(node, data_input):
    data = data_input
    return resolve(node)

def resolve(node):
    if len(node) == 1: return node[0] #special case for integers
    return func_list[node[0]](*node[1:])

data = [6,22,8]

func_list = [intInsert,dataInsert,add,sub,mul,div,ifStatement]

def makeReadable(node, depth=0):
    """ preorder search the tree and produce readable stuff """
    prog = "\n" + ".   "*depth + "("
    if len(node) == 1:
        return prog + repr(node[0]) + ")"
    
    prog += func_list[node[0]].__doc__
    for i in range(1, len(node)):
        prog += makeReadable(node[i], depth+1) + ")"
    return prog
