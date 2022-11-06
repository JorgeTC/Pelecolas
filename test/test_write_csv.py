from src.blog_csv_mgr import BlogCsvMgr


def test_write_csv():
    # Escribo el csv
    BlogCsvMgr.write_csv()
    # Extraigo el contenido
    content = BlogCsvMgr.open_to_read()
    # que me espero que no sea vacío
    assert len(content) != 0

    # como lo acabo de escribir me espero que no sea necesario
    assert BlogCsvMgr.is_needed() == False
