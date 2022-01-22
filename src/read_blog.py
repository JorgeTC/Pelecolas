import re

class ReadBlog():

    BLOG_MONTH = 'https://pelecolas.blogspot.com/{}/{:02d}/'.format

    def get_director_year_from_content(self, content: str):
        '''
        Dado el contenido de un post de mi blog,
        extraigo el año de la película y el director
        '''
        divs = content.find_all('div')
        # Quiero director
        director = re.search('Dir.: (.*)', divs[0].contents[1].contents[0]).group(1)
        director = director.strip()
        # Quiero año
        año = re.search('(\d{4})', divs[1].contents[1].contents[0]).group(1)

        return director, año
