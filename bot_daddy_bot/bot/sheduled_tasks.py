import aiocron
from ..config import flood_col, colh
from .her import HerGame


@aiocron.crontab('0 */6 * * *')
async def update_flood():
    flood_col.replace_one({'users': {'$exists': True}},
                          {'users': []})


@aiocron.crontab('0 0 * * *')
async def update_bydlos():
    groups = []
    for doc in colh.find({'group': {'$exists': True}}):
        if doc['group'] not in groups:
            groups.append(doc['group'])
    for group in groups:
        await HerGame(chat_id=group).reset_her()
