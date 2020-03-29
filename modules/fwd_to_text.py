from aiogram.utils import exceptions
import typing
from config import SERVICE_ACCOUNT_ID, bot, col_groups_users


class ForwardsToText:
    def __init__(self, chat_id, first_fwd_msg_id, last_fwd_msg_id):
        self.chat_id = chat_id
        self.first_fwd_msg_id = first_fwd_msg_id
        self.last_fwd_msg_id = last_fwd_msg_id

    async def get_monolog(self):
        result = ''
        forwarded_messages = range(self.first_fwd_msg_id + 1, self.last_fwd_msg_id)
        if len(forwarded_messages) == 0:
            return 'No messages found'
        for i in forwarded_messages:
            try:
                m = await bot.forward_message(self.chat_id, self.chat_id, i, disable_notification=True)
                msg_text = m.html_text
                await bot.delete_message(self.chat_id, m.message_id)
                result += f'{msg_text}\n'
            except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
                pass
        return result

    async def get_dialog(self, markers_dictionary: dict = None, mode: str = None):
        mode = mode or 'anonimous'
        if mode == 'public':
            return await self.get_public_dialog()
        def_xyz = ['x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']
        xyz = markers_dictionary or def_xyz
        result = ''
        forwarded_messages = range(self.first_fwd_msg_id + 1, self.last_fwd_msg_id)
        if len(forwarded_messages) == 0:
            return 'No messages found'
        senders_by_xyz = {}
        senders = []
        senders_quant = 0
        for i in forwarded_messages:
            try:
                m = await bot.forward_message(self.chat_id, self.chat_id, i, disable_notification=True)
                msg_text = m.html_text
                sender = m.forward_from or m.forward_sender_name or m.from_user
                sender = sender if isinstance(sender, str) else sender.id
                if sender in senders:
                    xxx = senders_by_xyz[sender]
                else:
                    if senders_quant == len(xyz):
                        return (f'Извините, максимально количество учатников - {len(xyz)}.\n\n'
                                f'Вы можете добавить свой словарь с любым количеством участников в меню настроек: '
                                f'/fwd_to_text (количество участников зависит от количества знаков в словаре)')
                    xxx = xyz[senders_quant]
                    senders_by_xyz[sender] = xxx
                    senders.append(sender)
                    senders_quant += 1

                await bot.delete_message(m.chat.id, m.message_id)
                result += f'{xxx*3}: {msg_text}\n'
            except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
                pass
        return result

    async def get_public_dialog(self):
        result = ''
        forwarded_messages = range(self.first_fwd_msg_id + 1, self.last_fwd_msg_id)
        if len(forwarded_messages) == 0:
            return 'No messages found'
        for i in forwarded_messages:
            try:
                m = await bot.forward_message(self.chat_id, self.chat_id, i, disable_notification=True)
                msg_text = m.html_text
                sender = m.forward_from or m.forward_sender_name or m.from_user
                sender_name = sender if isinstance(sender, str) else sender.first_name
                await bot.delete_message(m.chat.id, m.message_id)
                result += f'{sender_name}: {msg_text}\n'
            except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
                pass
        return result

    @staticmethod
    async def check_markers_dict(markers_dict: typing.Sequence[str]):
        if not isinstance(markers_dict, list):
            raise Exception('check_markers_dict: markers_dict argument must be list or string')
        markers_dict = [i.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') for i in markers_dict]
        wrong_markers = []
        for i in markers_dict:
            try:
                await bot.send_message(SERVICE_ACCOUNT_ID, i*3, parse_mode='html')
            except:
                wrong_markers.append(i)
        for i in wrong_markers:
            del markers_dict[markers_dict.index(i)]
        return {'markers_dict': markers_dict,
                'wrong_markers': wrong_markers}


class ForwardsToTextDB:
    def __init__(self):
        self.collection = col_groups_users

    def get_dictionary(self, dict_id: int, is_global: bool, user_id: int = None, user=None):
        """
        user: should be instance of fwd_to_text.ForwardsToTextUser

        returns: [str] --> markers_dictionary, example: ['x', 'y', 'z']
        """
        if is_global:
            global_dictionaries = self.get_global_dictionaries()
            for dic in global_dictionaries:
                if dic.id == dict_id:
                    return dic

        if user and not isinstance(user, ForwardsToTextUser):
            raise Exception('user should be instance of fwd_to_text.ForwardsToTextUser')
        user_dictionaries = ForwardsToTextUser(user_id).dictionaries if user_id else user.dictionaries
        for dic in user_dictionaries:
            if dic.id == dict_id:
                return dic

    def get_global_dictionaries(self):
        doc = self.collection.find_one({'user': 'fwd_to_text'})
        return [ForwardsToTextDictionary(**i, is_global=True) for i in doc['fwd_to_text']['markers_dicts']]


class ForwardsToTextUser(ForwardsToTextDB):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        document = self.collection.find_one({'user': user_id})

        if not document:
            self.collection.insert_one({'user': user_id,
                                        'fwd_to_text':
                                            {'markers_dicts': [],
                                             'default_dict': {'is_global': True,
                                                              'dict_id': 0},
                                             'default_mode': 'anonimous'}
                                        })
            document = self.collection.find_one({'user': user_id})

        if not document.get('fwd_to_text'):
            document['fwd_to_text'] = {'markers_dicts': [],
                                       'default_dict': {'is_global': True,
                                                        'dict_id': 0},
                                       'default_mode': 'anonimous'}
            self.collection.replace_one({'user': user_id}, document)

        self.full_doc = document
        document = document['fwd_to_text']

        self.document = document
        self.dictionaries = [ForwardsToTextDictionary(**i, is_global=False) for i in document['markers_dicts']]
        self.default_dict = ForwardsToTextDictionary(**document['default_dict'])
        self.default_mode = document['default_mode']

    def set_default_mode(self, default_mode: str, update_db: bool = True):
        self.default_mode = default_mode
        self.document['default_mode'] = self.default_mode
        if update_db:
            self.full_doc['fwd_to_text'] = self.document
            self.collection.replace_one({'user': self.user_id}, self.full_doc)

    def delete_dictionary(self, dict_id: int):
        for dic in self.dictionaries:
            if dic.id == dict_id:
                if self.default_dict.id == dic.id and not self.default_dict.is_global:
                    xyz_global_dic = self.get_dictionary(dict_id=0, is_global=True, user=self)
                    self.set_default_dict(dictionary=xyz_global_dic)
                del self.dictionaries[self.dictionaries.index(dic)]
                self.document['markers_dicts'] = [{'id': i.id, 'name': i.name, 'dictionary': i.markers} for i in self.dictionaries]
                break
        self.full_doc['fwd_to_text'] = self.document
        self.collection.replace_one({'user': self.user_id}, self.full_doc)

    def set_default_dict(self, dict_id: int = None, is_global: bool = None, dictionary=None, update_db=True):
        """
        dictionary: should be an instance of ForwardsToTextDictionary with is_global not None
        """
        if dictionary:
            dict_id = dictionary.id
            is_global = dictionary.is_global
        if is_global is None:
            raise Exception('is_global mustn\'t be None')
        self.default_dict = {'dict_id': dict_id,
                             'is_global': is_global}
        self.document['default_dict'] = self.default_dict
        if update_db:
            self.full_doc['fwd_to_text'] = self.document
            self.collection.replace_one({'user': self.user_id}, self.full_doc)

    async def add_dictionary(self, name: str, markers: typing.Sequence):
        check_results = await ForwardsToText.check_markers_dict(markers_dict=markers)
        if not check_results['markers_dict']:
            raise AllMarkersWrong
        new_markers_dict_id = self.dictionaries[-1]['id'] + 1 if self.dictionaries else 0
        new_dictionary = {'id': new_markers_dict_id,
                          'name': name,
                          'dictionary': check_results['markers_dict']}
        self.dictionaries.append(ForwardsToTextDictionary(**new_dictionary))
        self.document['markers_dicts'].append(new_dictionary)
        self.full_doc['fwd_to_text'] = self.document
        self.collection.replace_one({'user': self.user_id}, self.full_doc)
        return (ForwardsToTextDictionary(**new_dictionary), check_results['wrong_markers'])


class ForwardsToTextDictionary:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        if self.id is None:
            self.id = kwargs.get('dict_id')
        self.name = kwargs.get('name')
        self.markers = kwargs.get('dictionary')
        self.is_global = kwargs.get('is_global')


class AllMarkersWrong(Exception):
    def __init__(self, text=None):
        self.txt = text


__all__ = ['ForwardsToTextDictionary',
           'ForwardsToText',
           'ForwardsToTextDB',
           'ForwardsToTextUser',
           'AllMarkersWrong']
