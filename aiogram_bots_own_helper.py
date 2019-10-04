import traceback
import time
import pymongo
import os

client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
colh = db.her_morzhovij


async def cut_message(message_text, limitation):
    try:
        x = 0
        y = 0
        italic_op = 0
        bold_op = 0
        italic_cl = 0
        bold_cl = 0
        cuted_text = ''
        added_tag = None
        it = list(message_text)
        for i in it:
            if y <= limitation:
                if limitation - y <= 2 and italic_op == italic_cl and bold_op == bold_cl:
                    if i == 'i':
                        cuted_text += 'i></i>'
                    elif i == 'b':
                        cuted_text += 'b></b>'
                    elif i == '>':
                        cuted_text += f'{i}</{x[-1]}>'
                    x += 1
                    break
                else:
                    cuted_text += i
                if it[x-2] + it[x-1] + i not in ['<i>', '<b>'] and it[x-3] + it[x-2] + it[x-1] + i not in ['</i>', '</b>']:
                    y += 1
                elif it[x-2] + it[x-1] + i == '<i>':
                    italic_op += 1
                elif it[x-2] + it[x-1] + i == '<b>':
                    bold_op += 1
                elif it[x-3] + it[x-2] + it[x-1] + i == '</i>':
                    italic_cl += 1
                elif it[x-3] + it[x-2] + it[x-1] + i == '</b>':
                    bold_cl += 1
                x += 1
            elif italic_op == italic_cl and bold_op == bold_cl:
                    break
            else:
                if italic_op != italic_cl:
                    if i == '<':
                        cuted_text += '</i>'
                        x += 4
                    elif i == '/':
                        cuted_text += '/i>'
                        x += 3
                    elif i == 'i':
                        cuted_text += 'i>'
                        x += 2
                    elif i == '>':
                        cuted_text += '>'
                        x += 1
                    else:
                        cuted_text += '</i>'
                        added_tag = '</i>'
                if bold_op != bold_cl:
                    if i == '<':
                        cuted_text += '</b>'
                        x += 4
                    elif i == '/':
                        cuted_text += '/b>'
                        x += 3
                    elif i == 'b':
                        cuted_text += 'b>'
                        x += 2
                    elif i == '>':
                        cuted_text += '>'
                        x += 1
                    else:
                        cuted_text += '</b>'
                        added_tag = '</b>'
                break
        return {'cuted': cuted_text,
                'len_cuted': x,
                'added_tag_at_end': added_tag}
    except:
        print(traceback.format_exc())
        raise Exception('MessageNotCuted')

async def cut_for_messages(message_text, limitation):
    try:
        currently_cuted = 0
        message_parts = []
        added_tag_at_last = None
        while len(message_text) > currently_cuted:
            cut_message_result = await cut_message(message_text, limitation)
            currently_cuted += cut_message_result['len_cuted']
            if added_tag_at_last:
                cuted_part = added_tag_at_last.replace('/', '')
                cuted_part += cut_message_result['cuted']
                added_tag_at_last = None
            else:
                cuted_part = cut_message_result['cuted']
            if cut_message_result['added_tag_at_end']:
                added_tag_at_last = cut_message_result['added_tag_at_end']
            message_parts.append(cuted_part)
            message_text = message_text[currently_cuted:]
            limitation = len(message_text) if limitation < len(message_text) else limitation
        return message_parts
    except:
        print(traceback.format_exc())

async def get_complex_argument(message_text):
    args_list = message_text.split()[1:]
    last_word = args_list[-1]
    argument = ''
    for word in args_list:
        if word != last_word:
            argument += word + ' '
        else:
            argument += word
    return argument

def check_date(date):
    if time.time() - date.timestamp() < 172800:
        return True

async def reset_her(chat_id):
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
    colh.replace_one(future_doc,
                     {'bydlos': 'future',
                      'group': chat_id})


async def fwd_to_text(forwarded_message):
    text = forwarded_message.text
    return text
