from ..core import DicAcademicBase, WordResult


class LopatinDic(DicAcademicBase):
    def __init__(self):
        super().__init__()

    def get_word_results(self, q: str):
        results = self.request(dic='lopatin', q=q)
        return [WordResult(result) for result in results]
