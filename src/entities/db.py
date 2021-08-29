import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from entities.player import Player
from entities.army import Army
from entities.war import War

cred = credentials.Certificate("src\env\commander-a29a6-firebase-adminsdk-umqv3-91332b1308.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def create_war(guild_id, war):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war.title)
    doc_ref.set({
        u'title': war.title,
        u'region': war.region,
        u'date': war.date,
        u'attackers': war.attackers,
        u'defenders': war.defenders,
    })
    create_army(guild_id,war,war.army)
    return

def create_army(guild_id, war, army):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war.title)
    col_ref = doc_ref.collection(u'army')
    for g in range(0,len(army.comp)):
        group = col_ref.document(u'group ' + str(g + 1))
        group.set({})
        for p in range(0,len(army.comp[g])):
            group.update(
                {str(p+1) : {
                    u'name' : army.comp[g][p].name,    
                    u'lvl' : army.comp[g][p].lvl,    
                    u'role' : army.comp[g][p].role,
                    u'primary' : army.comp[g][p].primary,
                    u'secundary' : army.comp[g][p].secundary
                }
            })
    army_info = doc_ref.collection(u'armyInfo')
    army_info.document(u'weapons').set(army.weapons)
    army_info.document(u'roles').set(army.roles)
    army_info.document(u'lvl').set(army.lvl)
    return

def load_war(guild_id, war_title):
    army = load_army(guild_id,war_title)
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war_title).get().to_dict()
    war = War(title = doc_ref['title'], region = doc_ref['region'], date = doc_ref['date'], attackers = doc_ref['attackers'], defenders = doc_ref['defenders'], army = army)
    return war

def load_army(guild_id, war_title):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war_title)
    army_ref = doc_ref.collection(u'army').stream()
    comp = [[None for p in range(5) ] for g in range(10) ]
    for group in army_ref:
        group_number = int(group.id.replace('group ','')) - 1
        group_dic = group.to_dict()
        for pos in range(1,6):
            comp[group_number][pos-1] = Player(name = group_dic[str(pos)]['name'], 
                lvl = group_dic[str(pos)]['lvl'], 
                role = group_dic[str(pos)]['role'], 
                primary = group_dic[str(pos)]['primary'], 
                secundary = group_dic[str(pos)]['secundary'])
    info_ref = doc_ref.collection(u'armyInfo')
    weapons = info_ref.document(u'weapons').get().to_dict()
    roles = info_ref.document(u'roles').get().to_dict()
    lvl = info_ref.document(u'lvl').get().to_dict()
    return Army(comp, roles, weapons, lvl)

def update_army_info(army, war_ref):
    armyInfo = Army.recalculate_info(army)
    army_info = war_ref.collection(u'armyInfo')
    army_info.document(u'weapons').set(armyInfo.weapons)
    army_info.document(u'roles').set(armyInfo.roles)
    army_info.document(u'lvl').set(armyInfo.lvl)
    return

def enlist(guild_id, war_title, army, player, group, pos):
    war_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war_title)
    if group == 0 or pos == 0:
        for g in army.comp:
            index = next((i for i,p in enumerate(g) if p.name == '-'), None) # gets the next available spot for player to enter
            if index != None:
                group = army.comp.index(g) + 1
                pos = index + 1
                break
    army.comp[int(group)-1][int(pos)-1] = player
    group = war_ref.collection(u'army').document(f'group {group}')
    group.update(
        {str(pos) : {
            u'name' : player.name,    
            u'lvl' : player.lvl,    
            u'role' : player.role,
            u'primary' : player.primary,
            u'secundary' : player.secundary
        }
    })
    update_army_info(army, war_ref)
    
    #Criar erro para caso nao tenha lugar vazio
    return