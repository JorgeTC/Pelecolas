from dlg_scroll_base import DlgScrollBase

class YesNo(DlgScrollBase):
    def __init__(self, question) -> None:
        self.sz_question = question
        self.sz_options = ["Sí", "No"]
        self.n_options = 2
        self.curr_index = 1
        self.min_index = 0

    def get_ans(self):
        ans = DlgScrollBase.get_ans(self)

        return ans == "Sí"

