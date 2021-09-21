from os import name
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from entities.player import Player
from entities.army import Army
from entities.war import War

cred = credentials.Certificate("src\env\commander-a29a6-firebase-adminsdk-umqv3-91332b1308.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def init_guild(guild_id):
    db.collection(u'guilds').document(str(guild_id)).set({"war_count" : 0})
    return

def add_member(guild_id, user_id, player):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'members').document(str(user_id))
    doc_ref.set(vars(player))
    return

def save_war(guild_id, war):
    guild_ref = db.collection(u'guilds').document(str(guild_id))
    war_count = update_war_count(guild_ref)
    war_number = war_count + 1
    war_ref = guild_ref.collection(u'wars').document(str(war_number))
    war_ref.set({
        u'title': war.title,
        u'region': war.region,
        u'date': war.date,
        u'attackers': war.attackers,
        u'defenders': war.defenders,
        u'outcome' : war.outcome
    })
    save_army(guild_id, war.army, war_number)
    update_war_count(guild_ref)
    return war_number

def save_army(guild_id, army, war_number):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(str(war_number))
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
                    u'weapon' : army.comp[g][p].weapon
                }
            })
    army_info = doc_ref.collection(u'armyInfo')
    army_info.document(u'weapons').set(army.weapons)
    army_info.document(u'roles').set(army.roles)
    army_info.document(u'lvl').set(army.lvl)
    return

def load_war(guild_id, war_number):
    army = load_army(guild_id, war_number)
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(str(war_number)).get().to_dict()
    war = War(title = doc_ref['title'], region = doc_ref['region'], date = doc_ref['date'], attackers = doc_ref['attackers'], defenders = doc_ref['defenders'], army = army, outcome=doc_ref['outcome'])
    return war

def load_army(guild_id, war_number):
    doc_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(str(war_number))
    army_ref = doc_ref.collection(u'army').stream()
    comp = [[None for p in range(5) ] for g in range(10) ]
    for group in army_ref:
        group_number = int(group.id.replace('group ','')) - 1
        group_dic = group.to_dict()
        for pos in range(1,6):
            comp[group_number][pos-1] = Player(name = group_dic[str(pos)]['name'], 
                lvl = group_dic[str(pos)]['lvl'], 
                role = group_dic[str(pos)]['role'], 
                weapon = group_dic[str(pos)]['weapon'])
    info_ref = doc_ref.collection(u'armyInfo')
    weapons = info_ref.document(u'weapons').get().to_dict()
    roles = info_ref.document(u'roles').get().to_dict()
    lvl = info_ref.document(u'lvl').get().to_dict()
    return Army(comp, roles, weapons, lvl)

def load_char(guild_id, user_id):
    member = db.collection(u'guilds').document(str(guild_id)).collection(u'members').document(str(user_id)).get()
    if member.exists:
        char = Player.from_dict(member.to_dict())
    else:
        char = None
    return char

def wars_list(guild_id):
    ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').get()
    valid_wars = [war.id for war in ref]
    return valid_wars

def all_wars(guild_id):
    unfinished_wars = []
    finished_wars = []
    query = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').stream() #get wars where outcome is ''
    for war in query:
        w = war.to_dict()
        w['id'] = war.id
        if w['outcome'] == '':
            unfinished_wars.append(w)
        else:
            finished_wars.append(w)
    return unfinished_wars , finished_wars

def update_army_info(army, war_ref):
    armyInfo = Army.recalculate_info(army)
    army_info = war_ref.collection(u'armyInfo')
    army_info.document(u'weapons').set(armyInfo.weapons)
    army_info.document(u'roles').set(armyInfo.roles)
    army_info.document(u'lvl').set(armyInfo.lvl)
    return

def update_war_count(guild_ref):
    qtd = len(guild_ref.collection(u'wars').get())
    guild_ref.update({u'war_count' : qtd})
    return qtd

def enlist(guild_id, war_number, army, player, group, pos):
    war_ref = db.collection(u'guilds').document(str(guild_id)).collection(u'wars').document(str(war_number))
    if group == 0 or pos == 0:
        for g in army.comp:
            index = next((i for i,p in enumerate(g) if p.name == '-'), None) # gets the next available spot for player to enter
            if index != None:
                group = army.comp.index(g) + 1
                pos = index + 1
                break
    if group > 0 and group <= 10 and pos > 0 and pos <= 5:
        army.comp[int(group)-1][int(pos)-1] = player
        group = war_ref.collection(u'army').document(f'group {group}')
        group.update(
            {str(pos) : {
                u'name' : player.name,    
                u'lvl' : player.lvl,    
                u'role' : player.role,
                u'weapon' : player.weapon
            }
        })
        update_army_info(army, war_ref)
        return False
    else: #error for when war is already full of players
        return True