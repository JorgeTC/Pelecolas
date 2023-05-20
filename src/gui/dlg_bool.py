from .dlg_scroll_base import DlgScrollBase


class YesNo(DlgScrollBase):
    def __init__(self, question: str, empty_ans: bool = False) -> None:
        DlgScrollBase.__init__(self, question, ["Sí", "No"], empty_ans=empty_ans)

    def get_ans(self) -> bool:
        ans = DlgScrollBase.get_ans(self)

        return ans == "Sí"
