#!/usr/bin/env python
# coding: utf-8

# In[127]:


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time


# In[128]:


from ebooklib import epub


# In[129]:


# form HTTP request
req = Request('http://paulgraham.com/articles.html')
# Read the contents of the html
content = urlopen(req).read()
# format the contents
doc = BeautifulSoup(content)


# In[130]:


# Get the links
the_links = np.array([])
for link in doc.find_all('a')[4:-6]:
    the_links = np.append(the_links, link.get('href'))


# In[131]:


# Get the titles
titles = np.array([])
for link in doc.find_all('a')[4:-6]:
    titles = np.append(titles, link.get_text())


# In[132]:


# make a dataframe with said data
titles_and_links = pd.DataFrame()
titles_and_links['titles'] = titles
titles_and_links['link'] = the_links
# eyeball inspect
titles_and_links.to_csv('test.csv')


# In[436]:


start_time = time.time()
article_n = len(titles_and_links)
book = epub.EpubBook()

# add metadata
book.set_identifier(uuid.uuid4().hex)
book.set_title('Paul Graham Essays')
book.set_language('en')
book.add_author('Paul Graham')


# In[437]:


# download all the html from each link, text only
for i in range(article_n):
    content = urlopen(Request('http://paulgraham.com/' + titles_and_links['link'][i])).read()
    article = BeautifulSoup(content)
    globals()[f"chapter{i}"] = epub.EpubHtml(title=titles_and_links['titles'][i], file_name=(titles_and_links['titles'][i]+'.xhtml'), lang='en')
    globals()[f"chapter{i}"].content = article.prettify()
    book.add_item(globals()[f"chapter{i}"])


# In[438]:


book.toc = (tuple([globals()['chapter' + str(i)] for i in range(article_n)]))
            
# add navigation files
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())


# In[439]:


# define css style
style = '''
@namespace epub "http://www.idpf.org/2007/ops";
body {
font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
 text-align: left;
 text-transform: uppercase;
 font-weight: 200;     
}
ol {
    list-style-type: none;
}
ol > li:first-child {
    margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
    margin-top: 0.3em;
}
'''

# add css file
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

# create spine
book.spine = ['nav'] + [globals()['chapter' + str(i)] for i in range(article_n)]

# create epub file
epub.write_epub('test.epub', book, {})
print("--- %s seconds ---" % (time.time() - start_time))

