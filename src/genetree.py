import random
import funclist
import math
import inspect

from pyevolve import Util
from pyevolve import Consts
class GeneFunctionTree():

    def __init__(self):
        self.length     =  0
        self.MAX_RANDOM =  101
        self.MIN_RANDOM = -100
        self.pmut       =  0.07
        self.gene = [0]
        self.mutateNode(self.gene)
        self.length = self.getLength(self.gene)
    
    def interpret(self):
        return funclist.resolve(self.gene)
        
    def __repr__(self):
        return "\n\n" + repr(self.gene) + "\n" + funclist.makeReadable(self.gene)



    def __preorder(self,node):
        if self.__counter == self.__target:
            return node
        self.__counter += 1
        for i in range(1, len(node)):
            newnode = self.__preorder(node[i])
            if newnode != None:
                return newnode
        return None

    def getLength(self,node):
        self.__target = -1
        self.__counter = 0
        self.__preorder(node)
        return self.__counter
        
    def pickRandomNode(self):
        # http://okmij.org/ftp/Scheme/random-tree-node.scm
        # or do the walk thing that bryce suggested because that lisp thing in the link hurts my mind / feelings
        # note to self: consider looking at that link again later ... it may prove to be faster than the double-walk

        # find the length of the tree - Should be a known value, we populate the tree and in a Tree class it stores the magic number
        # deal; the tree class is the Gene thing I'm working on now. Also, length is a magic number?
        self.__target = random.randint(0,self.length-1)
        # print "We are looking for the node:",self.__target
        self.__counter = 0
        # print "Starting preorder search"
        node = self.__preorder(self.gene)
        # print "picked the random node:", node
        return node
        
    def mutateNode(self, node):
        new_func_index = self.randomFunc()
        # print "Node under mutation:", node, "gene:", self.gene
        # print "Switching to new function:", funclist.func_list[new_func_index]
        
        if new_func_index == 0:
            # This is an integer node.
            number_of_args = 1
        else:
            node[0] = new_func_index
            # make sure that the new node has the correct number of resolvables.
            number_of_args = len(
                    inspect.getargspec(
                        funclist.func_list[new_func_index])[0]) + 1
        
        while len(node) > number_of_args:
            self.removeArg(node)
        while len(node) < number_of_args:
            self.addArg(node)
            
        # print "Mutation over, node:", node

    def removeArg(self, node):
        # remove one at random! this could destroy great swaths of logic! Oh well! That is evolution at work!
        arg_index = random.randint(1, len(node)-1)
        self.length -= self.getLength(node[arg_index])
        node.remove(node[arg_index])

    def addArg(self, node):
        # add one at random! Hmm, should we just add ints / data, or should we continue down the logic tree?
        # Lets try ints / data for now
        # this code sort of sucks as it relies on int / data inserts being 0 and 1 in the func_list. I don't care to revise it right now.
        # I can't think of a good way to fix it without slowing it down, and it needs to be fast! (Go python go!)
        if random.randint(0,1):
            new_node = self.createIntNode()
            self.length += 1
        else:
            new_node = self.createDataNode()
            self.length += 2
        # if we want to continue down the tree; we could add a chance of performing 'mutateNode' on the new node here
        node.insert(random.randint(1,len(node)),new_node)

    def createIntNode(self):
        return [random.randint(self.MIN_RANDOM,self.MAX_RANDOM)]

    def createDataNode(self):
        # although this is not strictly required I will give it a real data index number.
        # Just to be helpful.
        # I am truly a beneficient and caring creator of these blessed creatures
        # who shall endlessly fight to the death on my behalf.
        return [1, [random.randint(0, len(funclist.data))]]
        
    def randomInt(self):
        return random.randint(self.MIN_RANDOM, self.MAX_RANDOM)

    def randomFunc(self):
        ret = random.randint(0, len(funclist.func_list)-1)
        return ret
        # we may want to change this later, so that some functions are more or less likely to occur
        
    def mutateGene(self):
        # number of mutations! will be at least one.
        for i in range(0, int(round(math.ceil(self.pmut * self.length)))):
            # this can be improved by making it an iterable generator function
            self.mutateNode(self.pickRandomNode())
        return i + 1
            
if __name__ == "__main__":
    # remove this junk later
    
    gft = GeneFunctionTree()
    
    for j in xrange(0,1000):
        gft.initializeGene()
        for i in xrange(0,10):
            gft.mutateGene()
        
        #if j % 1000 == 0:
        print j, gft.length
        gft.interpret()
        
    print gft.gene
    
    print "is the same as:"
    print funclist.makeReadable(gft.gene)
    print "which produces:"
    
    print gft.interpret()
