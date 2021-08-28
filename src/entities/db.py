import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from entities.player import Player
from entities.war import Army
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
    army_info.document(u'weaponCount').set(army.weapon_count)
    army_info.document(u'roles').set({
            u'dps': army.dps,
            u'tanks': army.tanks,
            u'supports': army.supports
    })
    return

def load_army(guild_id, war_title):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(war_title)
    army_ref = doc_ref.collection(u'army').stream()
    comp = [[None]*5]*10
    for group in army_ref:
        group_number = int(group.id.replace('group ','')) - 1
        group_dic = group.to_dict()
        for pos in range(1,len(group_dic)+1):
            comp[group_number-1][pos-1] = Player(name = group_dic.get(str(pos))['name'], 
                lvl = group_dic[str(pos)]['lvl'], 
                role = group_dic[str(pos)]['role'], 
                primary = group_dic[str(pos)]['primary'], 
                secundary = group_dic[str(pos)]['secundary'])
    info_ref = doc_ref.collection(u'armyInfo').stream()
    # army = Army(comp)
    return
