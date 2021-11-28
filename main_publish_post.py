from dlg_config import manage_config

def main(argv):

    manage_config()

    from poster import Poster
    from content_mgr import ContentMgr

    mgr = ContentMgr(argv)
    post_data = mgr.get_content()
    post = Poster()
    post.add_post(title=post_data['title'],
                  content=post_data['content'],
                  labels=post_data['labels'])

if __name__ == '__main__':
    main(__file__)
