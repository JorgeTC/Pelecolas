import sys

from poster import Poster
from content_mgr import ContentMgr

def main(argv):
    mgr = ContentMgr(argv)
    tit, con = mgr.get_title_and_content()
    post = Poster()
    post.add_post(title=tit, content=con)

if __name__ == '__main__':
    a = sys.argv
    main(sys.argv)
