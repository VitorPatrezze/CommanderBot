class Player:
    def __init__(self,name,lvl,role,primary,secundary):
        self.name = name
        self.lvl = lvl
        self.role = role
        self.primary = primary
        self.secundary = secundary
    
    valid_weapons = ['sword and shield', 'rapier', 'hatchet', 'spear', 'great axe', 'warhammer', 'bow', 'musket', 'fire staff', 'life staff', 'ice gauntlet']

    valid_roles = ['tanks', 'supports', 'dps']

    maximum_level = 60