from poster import Poster
from content_mgr import ContentMgr
from dlg_config import manage_config

def main(argv):

    manage_config()


    mgr = ContentMgr(argv)
    tit, con = mgr.get_title_and_content()
    post = Poster()
    post.add_post(title=tit, content=con)

if __name__ == '__main__':
    main(__file__)
