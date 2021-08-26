import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("env\commander-a29a6-firebase-adminsdk-umqv3-91332b1308.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection(u'users').document(u'alovelace')
doc_ref.set({
    u'first': u'Ada',
    u'last': u'Lovelace',
    u'born': 1815
})