import firebase_admin
from entities.player import Player
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("src\env\commander-a29a6-firebase-adminsdk-umqv3-91332b1308.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_war(guild_id, war):
    doc_ref = db.collection(u'guilds').document(guild_id).collection(u'wars').document(war.title)
    doc_ref.set({
        u'title': war.title,
        u'region': war.region,
        u'date': war.date,
        u'attackers': war.attackers,
        u'defenders': war.defenders,
    })
    save_army(guild_id,war,war.army)

def save_army(guild_id, war, army):
    col_ref = db.collection(u'guilds').document(guild_id).collection(u'wars').document(war.title).collection(u'army')
    for g in range(0,len(army)):
        group = col_ref.document(u'group ' + str(g + 1))
        group.set({})
        for p in range(0,len(army[g])):
            group.update(
                {str(p+1) : {
                    u'name' : army[g][p].name,    
                    u'lvl' : army[g][p].lvl,    
                    u'role' : army[g][p].role,
                    u'primary' : army[g][p].primary,
                    u'secundary' : army[g][p].secundary
                }
            })
    return


# army = [[Player(name='nomeTeste',lvl='60',role='DPS',primary='bow',secundary='spear') for e in range(5)] for e in range(10)]

# doc_ref = db.collection(u'guilds').document(u'testGuild').collection(u'wars').document(u'Guerra Teste')
# doc_ref.set({
#     u'title': u'teste',
#     u'region': u'teste',
#     u'date': u'teste'
# })
# army = doc_ref.collection(u'army').set(army)

