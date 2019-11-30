import requests
import bs4
import asyncio
import sys


async def gramota_parse(word):
    g = requests.get(f'http://gramota.ru/slovari/dic/?word={word}&all=x')
    gsoup = bs4.BeautifulSoup(g.text, 'lxml')
    for tag in gsoup.find_all('span'):
        if 'class' in tag.attrs and tag.attrs['class'] == ['accent']:
            tag.string = str(tag.string).upper()
    for tag in gsoup.find_all('sup'):
        tag.string = ''
        print(tag)
    for tag in gsoup.find_all('br'):
        tag.append('\n')
    for tag in gsoup.find_all('accent'):
        tag.string = str(tag.string).upper()
    dict_names_list = ['Орфографический словарь', 'Большой толковый словарь', 'Управление в русском языке',
                       'Русское словесное ударение', 'Словарь имён собственных', 'Словарь синонимов',
                       'Синонимы: краткий справочник', 'Словарь антонимов', 'Словарь методических терминов',
                       'Словарь русских имён']
    x = 0
    for tag in gsoup.find_all('b'):
            if tag.string is None:
                tag.string = gsoup.select('b')[x].getText()
            if tag.string not in dict_names_list:
                tag.string = html_tags(str(tag.string))
                tag.string = f'<b>{tag.string}</b>'
                x += 1
    x = 0
    for tag in gsoup.find_all('i'):
        if tag.string is None:
            tag.string = gsoup.select('i')[x].getText()
        if '<b>' not in str(tag.string):
            tag.string = html_tags(str(tag.string))
            tag.string = f'<i>{tag.string}</i>'
        x += 1
    word_info = gsoup.select('div.block-content.inside')[0].getText()
    word_info = word_info.split('[помощь]\n\n\n\n')[1].split('\n\n\n\n\n\n')[0]
    return word_info


async def get_word_dict(word_info):
    if word_info.lower().startswith('искомое слово отсутствует'):
        return None
    else:
        word_info = word_info.replace('искомое слово отсутствует', 'None').replace('\n\n', '\n')

        orthographic = word_info.split('Орфографический словарь')[1].split('Большой толковый словарь')[0]
        explanatory = word_info.split('Большой толковый словарь')[1].split('Управление в русском языке')[0]
        proper_nouns = word_info.split('Словарь имён собственных')[1].split('Словарь синонимов')[0]
        synonyms = word_info.split('Словарь синонимов')[1].split('Синонимы: краткий справочник')[0]
        synonyms_short = word_info.split('Синонимы: краткий справочник')[1].split('Словарь антонимов')[0]
        antonyms = word_info.split('Словарь антонимов')[1].split('Словарь методических терминов')[0]
        terms = word_info.split('Словарь методических терминов')[1].split('Словарь русских имён')[0]
        russian_names = word_info.split('Словарь русских имён')[1]
        if explanatory and '\n<b>2. ' not in explanatory:
            init_exp = explanatory
            explanatory = explanatory.split('<b>1.</b> ')[0] + '\n'
            for i in range(1, 20):
                try:
                    explanatory += f'<b>{i}.</b> '+init_exp.split(f'<b>{i}.</b> ')[1].split(f'<b>{i+1}.</b> ')[0] + '\n'
                except IndexError:
                    break
        if terms and '\n<b>2. ' not in terms:
            init_terms = terms
            terms = terms.split('1. ')[0] + '\n'
            for i in range(1, 20):
                try:
                    terms += f'{i}. '+init_terms.split(f'{i}. ')[1].split(f'{i+1}. ')[0] + '\n'
                except IndexError:
                    break
        word_dict = {
            'orthographic': ["Орфографический", orthographic],
            'explanatory': ['Толковый', explanatory],
            'proper_nouns': ['Имена собственные', proper_nouns],
            'synonyms': ['Синонимы', synonyms],
            'synonyms_short': ['Короткая справка по синонимам', synonyms_short],
            'antonyms': ['Антонимы', antonyms],
            'terms': ['Термины', terms],
            'russian_names': ['Русские имена', russian_names]
        }
        return word_dict


async def get_html_for_similar(word):
    g = requests.get(f'http://gramota.ru/slovari/dic/?word={word}&all=x')
    gsoup = bs4.BeautifulSoup(g.text, 'html.parser')
    similar_html_list = str(gsoup.select('.block-content')[0]).split('/slovari/dic/?word=')[1:]
    sim_list = []
    for similar_html in similar_html_list:
        if 'all=x' in similar_html:
            similar_html = fix_encoding(similar_html.split('&amp;all=x"')[0])
            if similar_html not in sim_list:
                sim_list.append(similar_html)
    return sim_list


async def similar_words(word):
    sim_list = await get_html_for_similar(word)
    similar_word_str = ''
    x = 1
    y = len(sim_list)
    for word in sim_list:
        if y != x:
            similar_word_str += f'{word}, '
        else:
            similar_word_str += f'{word}.'
        x += 1
    return similar_word_str


def fix_encoding(text):
    try:
        text = text.encode('windows-1251').decode('utf-8')
    except:
        return text
    return text


def html_tags(text):
    if '<' in text:
        text = text.replace('<', '&lt;')
    if '>' in text:
        text = text.replace('>', '$gt;')
    return text
