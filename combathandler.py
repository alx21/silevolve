from silconstants import *
import character

debug = False

class CombatHandler():
    def __init__(self, teams):
        """ Takes care of combat and combat details. Takes a tuple of lists of teams to initiate. """
        self.teams = list((list(teams[0]), list(teams[1])))

            
    def __reset(self):
        """New round; reset all temporary character data"""
        for t in self.teams:
            for c in t:
                # AI data hook here
                c.pickStance()
                c.reset()
                
    def __setInitiative(self):
        """ Get initiative for each character. """
        for t in self.teams:
            for c in t:
                # set everybody's initiative
                c.setInit()
                c.setActionPenalty(c.pickNumberOfActions()*-1 + 1)
                if debug and c.getInit() == -1: print c.name, " botched his init"
            # sort the teams by initiative order
            t.sort(lambda x,y: cmp(x.getInit(), y.getInit()))
                
    def combatRound(self):
        # this would probably be faster if I degeneralized it down to 2 teams
        # give it a shot sometime, eh?
        
        if debug: print "******* STARTING NEW COMBAT ROUND *******"
        
        self.__removeDead()
        self.__reset()
        self.__setInitiative()
        
        i = 0
        index = []
        cslice = []
        for t in self.teams:
        
            if len(t) == 0:
                if debug: print "EMPTY TEAM, this fight is over!"
                return False
            
            # find the highest initiative
            i = max(i, t[-1].getInit())
            # set the search index for this team
            index.append(len(t) - 1)
        
        while i >= 0:
            cslice = []
        
            j = 0
            for t in self.teams:
                while index[j] >=0 and t[index[j]].getInit() == i:
                    cslice.append(t[index[j]])
                    index[j] -= 1
                j+=1
            # run a section of the combat round at this initiative slice
            if cslice:
                if debug: print "Running the combat which happens at initiative ", i
                self.__combatSlice(cslice)
            i -= 1
        
        return True
        
            
    def __combatSlice(self, cslice):
        """ Run all combat happening at a given initiative level """
        # This function must hit the attack buttons and provide a complete list
        # of enemies to the attacker.
        
        # I need to find a way to efficiently figure out which teamlists the 
        # character is NOT in ...
        # for now, this:
        
        # a list of attack damages to be applied later
        action_list = []
        # a list of people with free actions to parse
        free_strike_list = []
        
        for c in cslice:
            for a in range(0, c.action_penalty + 1):
                # loops over actions that the character is taking this turn
                enemies = self.__getEnemies(c)
                damage = c.attack(enemies,data=self.getAIData(c))
                if damage == None:
                    if debug: print "We're getting none damage types here ..."
                    continue
                action_list.append(damage)
                
        # Now apply all of the damages
        for d in action_list:
            # if debug: print "Applying damage! to", d.target.name
            if not d.applyDamage():
                # don't bother giving them a free strike if one is dead :P
                if d.attacker_gets_free_strike and not c.has_used_free_strike:
                    free_strike_list.append((c,d.target))
                if d.defender_gets_free_strike and not d.target.has_used_free_strike:
                    free_strike_list.append((d.target,c))
                
        # OK, let us do something for some simplicity here. Attackers will hit 
        # targets with free attacks as soon as possible. Defenders will hit 
        # attackers ASAP given the chance. Ok? Ok!
        
        action_list = []
        for a in free_strike_list:
            # skip any slippery dead players in the free action list
            if a[0].done or a[1].done or a[0].has_used_free_strike: continue
            
            if debug: print a[0].name, "gets a free strike against", a[1].name
        
            # we remove the action penalty temporarily because it shouldn't
            # apply to free actions. This is not the most graceful move ...
            # kind of an ugly hack to be honest. Maybe I should have an 'action'
            # class that removes actions from players and weapons ... why does
            # everything have to get so complicated? QQ
            
            temp_action_penalty = a[0].action_penalty
            a[0].setActionPenalty(0)
            
            a[0].attack(target=a[1],data=self.getAIData(a[0])).applyDamage()
            
            a[0].has_used_free_strike = True
            a[0].setActionPenalty(temp_action_penalty)
        
        
    def __removeCharacter(self, character):
        for t in self.teams:
            if character in t:
                t.remove(character)
    
    def __getEnemies(self, c):
        """ Find all of the enemies of a given character. Return them. """
        enemies = []
        for t in self.teams:
            if not c in t:
                for char in t:
                    if not char.done: enemies.append(char)
        return enemies
        
    def __removeDead(self):
        for t in self.teams:
            for c in t:
                if c.done:
                    self.__removeCharacter(c)
                    
    def getAIData(self, character):
        """
        Rough format of data:
        [0]: number of players listed. First is always you.
        [1:18]: your stuff
        [19]: number of weapons that you are holding
        [20 + (1:3)*n]: data on each weapon you have
        [24 and so on]: the same data, looped, for each enemy
        """
        ai_data = [0] + character.getAIData()
        
        for e in self.__getEnemies(character):
            ai_data += e.getAIData()
            ai_data[0] += 1
        
        return ai_data
