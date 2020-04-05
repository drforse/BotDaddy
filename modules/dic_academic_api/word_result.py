from . import DicAcademicBase


class WordResult(DicAcademicBase):
    def __init__(self, word_dict: dict):
        super().__init__()
        self.id = word_dict.get('id')
        self.value = word_dict.get('value')
        self.info = word_dict.get('info')

    def __str__(self):
        return self.to_json()
