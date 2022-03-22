from src.dlg_config import manage_config

def main(argv):

    manage_config()

    from src.poster import POSTER
    from src.content_mgr import ContentMgr

    mgr = ContentMgr()
    post_data = mgr.get_content()
    POSTER.add_post(title=post_data['title'],
                  content=post_data['content'],
                  labels=post_data['labels'])

if __name__ == '__main__':
    main(__file__)
