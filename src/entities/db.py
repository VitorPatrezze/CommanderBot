from os import name
import firebase_admin
from google.cloud.firestore_v1.async_client import AsyncClient
from firebase_admin import credentials
from firebase_admin import firestore
from entities.player import Player
from entities.army import Army
from entities.war import War
from pathlib import Path

db: AsyncClient = firestore.AsyncClient()


async def init_guild(guild_id):
    await db.collection("guilds").document(str(guild_id)).set({"war_count": 0})


async def delete_guild(guild_id):
    await db.collection("guilds").document(str(guild_id)).delete()


async def add_member(guild_id, user_id, player):
    doc_ref = (
        db.collection("guilds")
        .document(str(guild_id))
        .collection("members")
        .document(str(user_id))
    )
    await doc_ref.set(vars(player))


async def save_war(guild_id, war):
    guild_ref = db.collection("guilds").document(str(guild_id))
    war_count = await update_war_count(guild_ref)
    war_number = war_count + 1
    war_ref = guild_ref.collection("wars").document(str(war_number))
    await war_ref.set(
        {
            "title": war.title,
            "region": war.region,
            "date": war.date,
            "attackers": war.attackers,
            "defenders": war.defenders,
            "outcome": war.outcome,
        }
    )
    await save_army(guild_id, war.army, war_number)
    await update_war_count(guild_ref)
    return war_number


async def save_army(guild_id, army, war_number):
    doc_ref = (
        db.collection("guilds")
        .document(str(guild_id))
        .collection("wars")
        .document(str(war_number))
    )
    col_ref = doc_ref.collection("army")
    for g in range(0, len(army.comp)):
        group = col_ref.document("group " + str(g + 1))
        await group.set({})
        for p in range(0, len(army.comp[g])):
            await group.update(
                {
                    str(p + 1): {
                        "name": army.comp[g][p].name,
                        "lvl": army.comp[g][p].lvl,
                        "role": army.comp[g][p].role,
                        "weapon": army.comp[g][p].weapon,
                    }
                }
            )
    army_info = doc_ref.collection("armyInfo")
    await army_info.document("weapons").set(army.weapons)
    await army_info.document("roles").set(army.roles)
    await army_info.document("lvl").set(army.lvl)


async def load_war(guild_id, war_number):
    army = await load_army(guild_id, war_number)
    doc_ref = (
        await db.collection("guilds")
        .document(str(guild_id))
        .collection("wars")
        .document(str(war_number))
        .get()
    ).to_dict()
    war = War(
        title=doc_ref["title"],
        region=doc_ref["region"],
        date=doc_ref["date"],
        attackers=doc_ref["attackers"],
        defenders=doc_ref["defenders"],
        army=army,
        outcome=doc_ref["outcome"],
    )
    return war


async def load_army(guild_id, war_number):
    doc_ref = (
        db.collection("guilds")
        .document(str(guild_id))
        .collection("wars")
        .document(str(war_number))
    )
    army_ref = doc_ref.collection("army").stream()
    comp = [[None for p in range(5)] for g in range(10)]
    async for group in army_ref:
        group_number = int(group.id.replace("group ", "")) - 1
        group_dic = group.to_dict()
        for pos in range(1, 6):
            comp[group_number][pos - 1] = Player(
                name=group_dic[str(pos)]["name"],
                lvl=group_dic[str(pos)]["lvl"],
                role=group_dic[str(pos)]["role"],
                weapon=group_dic[str(pos)]["weapon"],
            )
    info_ref = doc_ref.collection("armyInfo")
    weapons = (await info_ref.document("weapons").get()).to_dict()
    roles = (await info_ref.document("roles").get()).to_dict()
    lvl = (await info_ref.document("lvl").get()).to_dict()
    return Army(comp, roles, weapons, lvl)


async def load_char(guild_id, user_id):
    member = (
        await db.collection("guilds")
        .document(str(guild_id))
        .collection("members")
        .document(str(user_id))
        .get()
    )
    if member.exists:
        char = Player.from_dict(member.to_dict())
    else:
        char = None
    return char


async def wars_ids_list(guild_id):
    ref = await db.collection("guilds").document(str(guild_id)).collection("wars").get()
    valid_wars = [war.id for war in ref]
    return valid_wars


async def all_wars(guild_id):
    unfinished_wars = []
    finished_wars = []
    query = (
        db.collection("guilds").document(str(guild_id)).collection("wars").stream()
    )  # get wars where outcome is ''
    async for war in query:
        w = war.to_dict()
        w["id"] = war.id
        if w["outcome"] == "":
            unfinished_wars.append(w)
        else:
            finished_wars.append(w)
    return unfinished_wars, finished_wars


async def update_army_info(army, war_ref):
    armyInfo = Army.recalculate_info(army)
    army_info = war_ref.collection("armyInfo")
    await army_info.document("weapons").set(armyInfo.weapons)
    await army_info.document("roles").set(armyInfo.roles)
    await army_info.document("lvl").set(armyInfo.lvl)
    return


async def update_war_count(guild_ref):
    qtd = len(await guild_ref.collection("wars").get())
    await guild_ref.update({"war_count": qtd})
    return qtd


async def update_war_outcome(guild_id, war_number, outcome):
    doc_ref = (
        db.collection("guilds")
        .document(str(guild_id))
        .collection("wars")
        .document(str(war_number))
    )
    await doc_ref.update({"outcome": outcome})


async def enlist(guild_id, war_number, army, player, group, pos):
    war_ref = (
        db.collection("guilds")
        .document(str(guild_id))
        .collection("wars")
        .document(str(war_number))
    )
    if group == 0 or pos == 0:
        for g in army.comp:
            index = next(
                (i for i, p in enumerate(g) if p.name == " - "), None
            )  # gets the next available spot for player to enter
            if index is not None:
                group = army.comp.index(g) + 1
                pos = index + 1
                break
    if 0 < group <= 10 and 0 < pos <= 5:
        army.comp[int(group) - 1][int(pos) - 1] = player
        group_ref = war_ref.collection("army").document(f"group {group}")
        await group_ref.update(
            {
                str(pos): {
                    "name": player.name,
                    "lvl": player.lvl,
                    "role": player.role,
                    "weapon": player.weapon,
                }
            }
        )
        await update_army_info(army, war_ref)
        return False, group, pos
    else:  # error for when war is already full of players
        return True, group, pos
