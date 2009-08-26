import character
import damage
import combathandler
import silconstants
import weaponlist

import funclist
import genetree

from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import Util

evolving_thug = character.Character( name    = "Geoff",
                                     weapons = [ weaponlist.hth(),
                                                 weaponlist.meleeWeapon(),
                                                 weaponlist.gun() ] )

simple_thug   = character.Character( name    = "Thug",
                                     weapons = [ weaponlist.meleeWeapon() ] )

def eval_func(chromosome):
    
    # populate the AI functions!
    evolving_thug.fillSlots(chromosome)
    
    for i in range(0, 100):
        
        # one hundred combats for each contestant!
        
        evolving_thug.clear()
        simple_thug.clear()
        
        team1 = [evolving_thug]
        team2 = [simple_thug]
        
        fight = combathandler.CombatHandler([team1, team2])
        
        score  = 0
        rounds = 0
        
        while fight.combatRound():
            # I might decide to add rounds of combat to the score some day
            rounds += 1
        
        if simple_thug.done:
            # one point for killing the other guy!
            score += 1
            
    return score
    
def initializeFuncTreeGenome(genome, **args):
    #genome.clearlist()
    for i in xrange(genome.listSize):
        genome.append(genetree.GeneFunctionTree())


def G1DListFuncTreeMutator(genome, **args):

    if args["pmut"] <= 0.0: return 0
    listSize = len(genome)
    mutations = args["pmut"] * (listSize)

    if mutations < 1.0:
        mutations = 1.0
        for it in xrange(listSize):
            if Util.randomFlipCoin(args["pmut"]):
                genome[it].mutateGene()
   
    else: 
       for it in xrange(int(round(mutations))):
           which_gene = rand_randint(0, listSize-1)
           genome[which_gene].mutateGene()

    return mutations


genome = G1DList.G1DList(5)
genome.evaluator.set(eval_func)
genome.initializator.set(initializeFuncTreeGenome)
genome.mutator.set(G1DListFuncTreeMutator)
ga = GSimpleGA.GSimpleGA(genome)
ga.setGenerations(1000)
ga.evolve(freq_stats=10)
open('best.p', 'wb').write(repr(ga.bestIndividual()))
print ga.bestIndividual()
