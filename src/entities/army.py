from entities.player import Player

class Army: 
    def __init__(self, comp, roles, weapons, lvl):
        self.comp = comp
        self.roles = roles
        self.weapons = weapons
        self.lvl = lvl
    
    def init_weapons():
        dicts = {}
        weapons = Player.valid_weapons
        for i in weapons:
            dicts[i] = 0
        return dicts

    def init_roles():
        dicts = {}
        roles = Player.valid_roles
        for i in roles:
            dicts[i] = 0
        return dicts   

    def init_lvl():
        dicts = {}
        roles = [60, 50, 40]
        for i in roles:
            dicts[str(i)] = 0
        return dicts  

    def create_army():
        comp = [[Player.null_player() for p in range(5)] for e in range(10)]
        army = Army(comp, Army.init_roles(), Army.init_weapons(), Army.init_lvl())
        return army

    def recalculate_info(army):
        army.lvl = Army.init_lvl()
        army.roles = Army.init_roles()
        army.weapons = Army.init_weapons()
        for g in army.comp:
            for p in g:
                if p.name != '-':
                    army.weapons[p.weapon] += 1
                    army.roles[p.role] += 1
                    if str(p.lvl) in army.lvl.keys():
                        army.lvl[str(p.lvl)] += 1
                    else:
                        army.lvl[str(p.lvl)] = 1
        return army
    
    def armyLvlString(dic):
        keyList = sorted(dic.keys(), key=int, reverse=True)
        string = '\n**Level Composition**\n'
        for k in keyList:
            string += f"`{dic[k]}x` {k}\n"
        return string
    
    def armyWeaponsString(dic):
        keyList = sorted(dic.keys(), reverse=True)
        string = '\n**Weapons**\n'
        for k in keyList:
            string += f"`{dic[k]}x` {k.capitalize()}\n"
        return string
    
    def armyRolesString(dic):
        keyList = sorted(dic.keys(), reverse=True)
        string = ''
        for k in keyList:
            string += f"\n`{dic[k]}x` **{k.capitalize()}**\n"
        return string

    def armyInfoString(army):
        string = ''
        string += Army.armyRolesString(army.roles)
        string += Army.armyWeaponsString(army.weapons)
        string += Army.armyLvlString(army.lvl)

        return string