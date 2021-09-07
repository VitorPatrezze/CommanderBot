class Player:
    def __init__(self,name,lvl,role,weapon):
        self.name = name
        self.lvl = lvl
        self.role = role
        self.weapon = weapon
    
    def from_dict(dict):
        name = dict['name']
        lvl = dict['lvl']
        role = dict['role']
        weapon = dict['weapon']
        return Player(name,lvl,role,weapon)

    def to_string(char):
        string = f"`{char.name} - {char.role.title()} - {char.weapon.title()} - level {char.lvl}`"
        return string

    def null_player():
        name = '-'
        lvl = ''
        role = ''
        weapon = ''
        return Player(name,lvl,role,weapon)

    valid_weapons = ['sword and shield', 'rapier', 'hatchet', 'spear', 'great axe', 'warhammer', 'bow', 'musket', 'fire staff', 'life staff', 'ice gauntlet']

    valid_roles = ['tanks', 'supports', 'dps']

    maximum_level = 60