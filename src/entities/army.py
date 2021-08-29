from entities.player import Player

class Army: 
    def __init__(self, comp, roles, weapons, lvl):
        self.comp = comp
        self.roles = roles
        self.weapons = weapons
        self.lvl = lvl
    
    def init_weapons():
        dicts = {}
        weapons = ['Sword and Shield', 'Rapier', 'Hatchet', 'Spear', 'Great Axe', 'War Hammer', 'Bow', 'Musket', 'Fire Staff', 'Life Staff', 'Ice Gauntlet']
        for i in weapons:
            dicts[i] = 0
        return dicts

    def init_roles():
        dicts = {}
        roles = ['Tanks', 'Supports', 'DPS']
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
        comp = [[Player(name='-',lvl='',role='',primary='',secundary='') for p in range(5)] for e in range(10)]
        army = Army(comp, Army.init_roles(), Army.init_weapons(), Army.init_lvl())
        return army

    def recalculate_info(army):
        army.lvl = Army.init_lvl()
        army.roles = Army.init_roles()
        army.weapons = Army.init_weapons()
        for g in army.comp:
            for p in g:
                if p.name != '-':
                    army.weapons[p.primary] += 1
                    army.roles[p.role] += 1
                    if p.lvl in army.lvl.keys():
                        army.lvl[p.lvl] += 1
                    else:
                        army.lvl[p.lvl] = 1
        return army
    
    def armyLvlString(dic):
        keyList = sorted(dic.keys(), key=int, reverse=True)
        string = '\n\n**Level Composition**\n'
        for k in keyList:
            string += f"`{dic[k]}x` {k}\n"
        return string

    def armyInfoString(army):
        ntanks = "`" + str(army.roles['Tanks']) + "x`"
        ndps = "`" + str(army.roles['DPS']) + "x`"
        nsupps = "`" + str(army.roles['Supports']) + "x`"
        nrapier = "`" + str(army.weapons['Rapier']) + "x`"
        nhatchet = "`" + str(army.weapons['Hatchet']) + "x`"
        nsword = "`" + str(army.weapons['Sword and Shield']) + "x`"
        nspear = "`" + str(army.weapons['Spear']) + "x`"
        ngreataxe = "`" + str(army.weapons['Great Axe']) + "x`"
        nwarhammer = "`" + str(army.weapons['War Hammer']) + "x`"
        nbow = "`" + str(army.weapons['Bow']) + "x`"
        nmusket = "`" + str(army.weapons['Musket']) + "x`"
        nfire = "`" + str(army.weapons['Fire Staff']) + "x`"
        nlife = "`" + str(army.weapons['Life Staff']) + "x`"
        nice = "`" + str(army.weapons['Ice Gauntlet']) + "x`"
        string = (
            f"\n**{ntanks} Tanks**\n"
            f"\n**{nsupps} Supports**\n"
            f"\n**{ndps} DPS**\n"
            f"\n**Weapons**\n"
            f"{nwarhammer} Warhammer\n"
            f"{ngreataxe} Greataxe\n"
            f"{nsword} Sword and Shield\n"
            f"{nlife} Life Staff\n"
            f"{nbow} Bow\n"
            f"{nfire} Fire Staff\n"
            f"{nhatchet} Hatchet\n"
            f"{nice} Ice Gauntlet\n"
            f"{nmusket} Musket\n"
            f"{nrapier} Rapier\n"
            f"{nspear} Spear\n"
            )
        string += Army.armyLvlString(army.lvl) 
        return string