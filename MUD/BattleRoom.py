import time
import random;

def currentTimeMillis():
    return int(round(time.time()*1000))    

class Entity:
    __name = "None"
    __health = 100
    __max_health = 100
    __damage = 10
    __hit_chance = 0.6
    
    #Kept in terms of milliseconds.
    __attack_rate = 1000 
    __heal_rate = 5000
	
    __start_time = 0
    __last_attack = 0
    __last_heal = 0

    # -1 : Do Nothing
    #  0 : Defend (take half damage)
    #  1 : Attack (if player attack random creature, if creature attack random player)
    #             (only once per attack_rate)
    #  2 : Heal (5 health, only once per heal_rate)
    __action = -1 # Ideally would have an enum for this
	

    def __init__(self, n, h, mh, d, hc, ar, hr):
        self.__name = str(n)
        self.__health = int(h)
        self.__max_health = int(mh)
        self.__damage = int(d)
        self.__hit_chance = float(hc)
        self.__attack_rate = int(ar)
        self.__heal_rate = int(hr)
        self.__start_time = currentTimeMillis()
	
    def getAction(self):
        return self.__action
	
    def getAttackRate(self):
        return self.__attack_rate
	
    def getDamage(self): 
        return self.__damage
	
    def getHealRate(self):
        return self.__heal_rate
	
    def getHealth(self):
        return self.__health;
	
    def getLastAttack(self):
        return self.__last_attack
	
    def getLastHeal(self):
        return self.__last_heal
	
    def getName(self):
        return self.__name
	
    def heal(self, time):
        self.__health += 5
        if (self.__health > self.__max_health):
            self.__health = self.__max_health
        self.__last_heal = time
	
    # Updates the value in action, if outside the allowed actions sets it to -1 (do nothing).
    def setAction(self, value):
        self.__action = value;
        if ((self.__action < -1) or (self.__action > 2)):
            self.__action = -1
	
    def setLastAttack(self, time):
        self.__last_attack = time
	
    def takeDamage(self, dmg):
        if (self.__action != 0):
            self.__health -= dmg
        else:  # We are defending.
            self.__health -= dmg//2
        if (self.__health < 0):
            self.__health = 0
#End Entity Class

# There should only be one of these running as the server and players can connect to it.
# So each team will need to make a Java/C/Python Server and client that can connec to any of the servers.
class Room:
    __creatures = []
    __players = []
    __messages = []
    __spawn_chance = 0.05

    # Kept in milliseconds.
    __check_spawn = 1000
	
    __presentTime = 0
    __creatureID = 1
	
    def __init__(self, sc, cs):
        self.__spawn_chance = sc;
        self.__check_spawn = cs;

    def addCreature(self, creature):
        self.__creatures.append(creature)
        self.__messages.append(creature.getName()+" has entered the room.")
        
    def addPlayer(self, player):
        self.__players.append(player)
        self.__messages.append(player.getName()+" has entered the room.")
	
    def attackRandomEntity(self, attacker, options):
        index = (int)(random.random()*len(options))
        target = options[index]
        targetHealth = target.getHealth()
        target.takeDamage(attacker.getDamage())
        self.__messages.append(attacker.getName()+" attacked "+target.getName()+" doing "+str(targetHealth - target.getHealth())+" damage.")
        attacker.setLastAttack(self.__presentTime);
        if (target.getHealth() == 0):
            options.pop(index)
            self.__messages.append(target.getName()+" killed.")

    def checkCreatureSpawn(self,lastSpawnCheck):
        if ((self.__presentTime - lastSpawnCheck) > self.__check_spawn): 
            check = random.random()
            if (self.__spawn_chance > check) :
                creature = Entity("Creature"+str(self.__creatureID),100,100,10,0.6,1000,5000)
                self.addCreature(creature)
                self.__creatureID += 1
            lastSpawnCheck = self.__presentTime
        return lastSpawnCheck

    def printMessages(self):
        while (len(self.__messages) > 0):
            msg = self.__messages.pop(0)
            print(msg)

    def process(self):
        self.processActions(self.__players,self.__creatures)
        self.processActions(self.__creatures,self.__players)
        
    def processActions(self,  entities, targets):
        for entity in entities:
            action = entity.getAction()
            if ((action == 1) and (len(targets) > 0)):
                lastAttack = entity.getLastAttack()
                if ((self.__presentTime - lastAttack) > entity.getAttackRate()):
                    self.attackRandomEntity(entity,targets)
            if (action == 2):
                lastHeal = entity.getLastHeal()
                if ((self.__presentTime - lastHeal) > entity.getHealRate()):
                    entityHealth = entity.getHealth()
                    entity.heal(self.__presentTime);
                    self.__messages.append(entity.getName()+" healed for "+str(entity.getHealth()-entityHealth));

    def setPresentTime(self,the_time):
        self.__presentTime = the_time
        
    def updateCreatureAction(self):
        for creature in self.__creatures:
            lastAttack = creature.getLastAttack();
            if ((self.__presentTime - lastAttack) > creature.getAttackRate()):
                creature.setAction(1) # Can attack so do that.
            else:
                lastHeal = creature.getLastHeal()
                if ((self.__presentTime - lastHeal) > creature.getHealRate()):
                    creature.setAction(2)  # If can't attack, but can heal do that.
                else:
                    creature.setAction(0)  # If can't attack or heal just defend.
#End Room Class

run = True

def createRoom(spawn_chance,check_spawn):
    return Room(spawn_chance,check_spawn)

def runGame(room):
    global run
    startTime = currentTimeMillis()
    lastSpawnCheck = startTime
    while (run):
        presentTime = currentTimeMillis()
        room.setPresentTime(presentTime)
        lastSpawnCheck = room.checkCreatureSpawn(lastSpawnCheck)		
        room.process()		
        room.updateCreatureAction()
        room.printMessages()



