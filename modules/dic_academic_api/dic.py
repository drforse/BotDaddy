from . import DicAcademicBase, WordResult


class Dic(DicAcademicBase):
    def __init__(self, dic: str):
        super().__init__()

    def get_word_results(self, q: str):
        results = self.request(dic=self.dic, q=q)
        return [WordResult(result) for result in results]
