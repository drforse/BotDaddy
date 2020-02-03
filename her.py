from config import bot, colh, compliments
import random
import traceback


class HerGame:
    def __init__(self, chat=None, chat_id=None):
        self.bydlo = None
        if chat:
            self.chat_id = chat.id
            self.chat_username = chat.username
        if chat_id:
            self.chat_id = chat_id
        
    async def get_today_bydlo(self, randomize=None):
        chat_id = self.chat_id
        chat_username = self.chat_username
        texts = []
        try:
            bydlos = colh.find_one({'bydlos': 'actual',
                                    'group': chat_id})
            if not bydlos or len(bydlos) == 3:  # if no doc in db or the document is quite empty, if its empty, could go wrong reset at night teoreticly
                await self.reset_her()
                bydlos = colh.find_one({'bydlos': 'actual',
                                        'group': chat_id})
            if 'done' not in bydlos:
                bydlos['done'] = False
            if not bydlos['done']:
                bydlos.pop('bydlos')
                bydlos.pop('group')
                bydlos.pop('_id')
                bydlos.pop('done')
                try:
                    bydlos.pop('compliment')
                except KeyError:
                    pass
                try:
                    bydlos.pop('last_bydlo')
                except KeyError:
                    pass
                if not randomize:
                    try:
                        texts = await self.get_bydlo(bydlos=bydlos, texts=texts)
                    except ValueError:
                        try:
                            texts = await self.get_random_bydlo(bydlos=list(list(bydlos.keys())), texts=texts)
                        except IndexError:
                            texts = await self.get_last_bydlo(texts=texts)
                    return texts
                else:
                    try:
                        texts = await self.get_random_bydlo(bydlos=list(list(bydlos.keys())), texts=texts)
                    except IndexError:
                        texts = await self.get_last_bydlo(texts=texts)
                    return texts
            else:
                random_id = int(random.random()*int(10**random.randint(1, 10)))
                main_bydlo_first_name = bydlos['done'].split(maxsplit=1)[1]
                doc = colh.find_one(bydlos)
                if 'compliment' in doc and doc['compliment']:
                    if chat_username:
                        texts.append(f'<a href="t.me/{chat_username}/{random_id}">Тык на сообщение с хером!</a>')
                        texts.append('...Ненавижу порталы!')
                        texts.append(f'{main_bydlo_first_name}, {main_bydlo_first_name}, {random.choice(compliments)}')
                    else:
                        texts.append(f'<a href="t.me/{chat_id}/{random_id}">Тык на сообщение с хером!</a>')
                        texts.append('...Ненавижу порталы!')
                        texts.append(f'{main_bydlo_first_name}, {main_bydlo_first_name}, {random.choice(compliments)}')
                else:
                    if chat_username:
                        texts.append(f'<a href="t.me/{chat_username}/{random_id}">Тык на сообщение с хером!</a>')
                        texts.append('...Ненавижу порталы!')
                        texts.append(f'{main_bydlo_first_name}, {main_bydlo_first_name}, вредный хуй!')
                    else:
                        texts.append(f'<a href="t.me/{chat_id}/{random_id}">Тык на сообщение с хером!</a>')
                        texts.append('...Ненавижу порталы!')
                        texts.append(f'{main_bydlo_first_name}, {main_bydlo_first_name}, вредный хуй!')
                return texts
        except:
            print(traceback.format_exc())
            raise Exception('Error while getting bydlo')

    async def get_last_bydlo(self, texts):
        chat_id = self.chat_id
        bydlos = colh.find_one({'bydlos': 'actual',
                                'group': chat_id})
        if 'done' in bydlos:
            last_bydlo = bydlos['last_bydlo'].split(maxsplit=1)[0]
            last_bydlo_first_name = bydlos['last_bydlo'].split(maxsplit=1)[1]
        else:
            bydlos = colh.find_one({'bydlos': 'future',
                                    'group': chat_id})
            last_bydlo = bydlos['last_bydlo'].split(maxsplit=1)[0]
            last_bydlo_first_name = bydlos['last_bydlo'].split(maxsplit=1)[1]
        texts.append(f'<a href="tg://user?id={int(last_bydlo)}">{last_bydlo_first_name},'
                     f' {last_bydlo_first_name}</a>, хер моржовый!')
        colh.update_one({'bydlos': 'actual',
                         'group': chat_id},
                        {'$set': {'done': f'{last_bydlo} {last_bydlo_first_name}'}})
        return texts

    async def get_random_bydlo(self, bydlos, texts):
        chat_id = self.chat_id
        texts.append('Итак, кто же у нас хер тут, м?')
        texts.append('Чекаю базу данных...')
        print(bydlos)
        main_bydlo = random.choice(bydlos)
        main_bydlo_member = await bot.get_chat_member(chat_id, int(main_bydlo))
        main_bydlo_first_name = main_bydlo_member.user.first_name
        texts.append(f'<a href="tg://user?id={int(main_bydlo)}">{main_bydlo_first_name},'
                     f' {main_bydlo_first_name}</a>, {random.choice(compliments)}!')
        colh.update_one({'bydlos': 'actual',
                         'group': chat_id},
                        {'$set': {'done': f'{main_bydlo} {main_bydlo_first_name}'}})
        colh.update_one({'bydlos': 'actual',
                         'group': chat_id},
                        {'$set': {'compliment': True}})
        return texts

    async def get_bydlo(self, bydlos, texts):
        chat_id = self.chat_id
        filtered_bydlos = {}
        print(bydlos)
        for bydlo in bydlos:
            print(type(bydlo))
            if bydlos[bydlo]['badmsgs'] > 0:
                allmsgs = bydlos[bydlo]['allmsgs']
                badmsgs = bydlos[bydlo]['badmsgs']
                percent = allmsgs / 100
                result = badmsgs / percent
                print(bydlos)
                filtered_bydlos[bydlo] = result
                print(filtered_bydlos)
        bydlo_bad_messages_value = max(list(filtered_bydlos.values()))
        texts.append('Итак, кто же у нас хер тут, м?')
        main_bydlos = []
        texts.append('Чекаю базу данных...')
        for bydlo, value in filtered_bydlos.items():
            if value == bydlo_bad_messages_value:
                main_bydlos.append(bydlo)
        if len(main_bydlos) > 1:
            main_bydlo = random.choice(main_bydlos)
            texts.append('Ну пиздец, вас тут сука несколько нахуй')
            texts.append('Кхм, прошу прощения, с волками жить...')
        else:
            print(main_bydlos)
            main_bydlo = main_bydlos[0]
        main_bydlo_member = await bot.get_chat_member(chat_id, int(main_bydlo))
        main_bydlo_first_name = main_bydlo_member.user.first_name
        texts.append(f'<a href="tg://user?id={int(main_bydlo)}">{main_bydlo_first_name},'
                     f' {main_bydlo_first_name}</a>, хер моржовый!')
        colh.update_one({'bydlos': 'actual',
                         'group': chat_id},
                        {'$set': {'done': f'{main_bydlo} {main_bydlo_first_name}'}})
        colh.update_one({'bydlos': 'actual',
                         'group': chat_id},
                        {'$set': {'compliment': None}})
        return texts

    async def reset_her(self):
        chat_id = self.chat_id
        actual_doc = colh.find_one({'bydlos': 'actual',
                                    'group': chat_id})
        future_doc = colh.find_one({'bydlos': 'future',
                                    'group': chat_id})
        if actual_doc is None:
            colh.insert_one({'bydlos': 'actual',
                             'group': chat_id})
            actual_doc = colh.find_one({'bydlos': 'actual',
                                        'group': chat_id})
        if future_doc is None:
            colh.insert_one({'bydlos': 'future',
                             'group': chat_id})
            future_doc = colh.find_one({'bydlos': 'future',
                                        'group': chat_id})
        actual_doc.pop('_id')
        future_doc.pop('_id')
        future_doc['bydlos'] = 'actual'
        colh.replace_one(actual_doc,
                         future_doc)
        future_doc['bydlos'] = 'future'
        print(future_doc)
        if 'done' in actual_doc:
            colh.replace_one(future_doc,
                             {'bydlos': 'future',
                              'group': chat_id,
                              'last_bydlo': actual_doc['done']})
        elif 'last_bydlo' in future_doc:
            colh.replace_one(future_doc,
                             {'bydlos': 'future',
                              'group': chat_id,
                              'last_bydlo': future_doc['last_bydlo']})
        else:
            colh.replace_one(future_doc,
                             {'bydlos': 'future',
                              'group': chat_id})
