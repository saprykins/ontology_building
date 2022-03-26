# Official doc arxiv: Request from api
# used to avoid arxiv overcharge
# import time

import urllib
import urllib.request

# Getting key information from xml
import xml.etree.ElementTree as ET

import requests

# Ontology
from owlready2 import *

# Text extraction
# import spacy
from pdfminer.high_level import extract_text

# 
# GET INFO ON ARTICLE FROM ARXIV SITE
# 

def get_article_data(url):
    # ex of API request
    # url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
    # url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=15'

    data = urllib.request.urlopen(url)
    # print(data.read().decode('utf-8'))

    tree = ET.parse(data)

    # putting article data in dictionary

    array_of_articles = []
    root = tree.getroot()
    # article_buffer = {}
    for child in root:

        article_buffer = {}
        art_authors = []
        for grand_child in child:

            # finds and updates article's link
            if grand_child.tag == '{http://www.w3.org/2005/Atom}id':
                article_link = grand_child.text
                pdf_link = article_link.replace(
                    'http://arxiv.org/abs', 'http://arxiv.org/pdf')
                article_buffer['pdf_link'] = pdf_link

            if grand_child.tag == '{http://www.w3.org/2005/Atom}title':
                article_buffer['title'] = grand_child.text

            if grand_child.tag == '{http://www.w3.org/2005/Atom}published':
                # in order to keep only the year
                article_buffer['published_on_date'] = grand_child.text[:4]

            if grand_child.tag == '{http://www.w3.org/2005/Atom}summary':
                article_buffer['summary'] = grand_child.text
            
            if grand_child.tag == '{http://arxiv.org/schemas/atom}comment':
                article_buffer['comment'] = grand_child.text
            
            if grand_child.tag == '{http://arxiv.org/schemas/atom}journal_ref':
                # we keep only the part related to the name of journal 
                # and don't keep page numbers
                journal_name_limiter = grand_child.text.find(')')
                journal_name = grand_child.text[:journal_name_limiter+1]
                article_buffer['journal_ref'] = journal_name
            
            # ::2 to avoid printing departments
            # for grand_grand_child in grand_child[::2]:
            author_dict = {}
            for grand_grand_child in grand_child:

                if grand_grand_child.tag == '{http://www.w3.org/2005/Atom}name':
                    writer = grand_grand_child.text
                    author_dict['name'] = writer
                    # print(writer)
                
                # some responses provide information on author's lab
                if grand_grand_child.tag == '{http://arxiv.org/schemas/atom}affiliation':
                    lab_of_writer = grand_grand_child.text
                    # print(lab_of_writer)
                    author_dict['lab'] = lab_of_writer
                    # print(lab_of_writer)
                
            # fill in the list of authors (each author is a dictionary with name and lab of the author)
            if author_dict:
                art_authors.append(author_dict)

            if article_buffer:
                article_buffer['authors'] = author_dict
            
            if len(art_authors) > 0:
                article_buffer['authors'] = art_authors
            
        # if dictionary is empty
        if article_buffer:
            array_of_articles.append(article_buffer)
    return array_of_articles



#
# TRANSFORMS REFERENCES (IN TEXT) FORMAT TO ARRAY OF AUTHORS
#

def line_of_authors_to_array(line):
    array_of_authors = []
    special_character ="&" # splits authors in references

    # if line.find('&') sometimes the last author is separated with sign symbol:
    if special_character in line:
        # print('1')
        last_author = line[line.find('&')+2:]
        line = line[:line.find('&')]
        array_of_authors.append(last_author.strip())

    while len(line)>3:
        # if find = -1 means that it did not find
        if line.find('.,') != -1:
            # print('2')
            # print('NOK')
            '''
            author_i = line[:line.find('.,')+1]
            # print(author_i)
            # if len(author_i)>6 and author_i[0] != ',':
            array_of_authors.append(author_i.strip())
            line = line[line.find('.,')+3:]
            '''
            author_i = line[:line.find('.,')+1].strip()
            # print(author_i)
            # if len(author_i)>8 and author_i[0] != ',':
            array_of_authors.append(author_i)
            
            line = line[line.find('.,')+3:]
            # if len(line)<8 and line[0] == ',':
            #     line = ''
        else:
            # print('3')
            # author_i = line_1
            array_of_authors.append(line.strip())
            line = ''

    return array_of_authors



# 
# GIVE A LINK WITH ARTICLE, GET REFERENCES IN TEXT
# 

def get_references_in_text_format_from_link(pdf_url):
    
    try:
        text = send_a_pdf_to_api_and_get_text_from_api(pdf_url)
        reference_word = 'Reference'
        references = text[text.find(reference_word):]
        
        # to exclude the work references itself
        # return references[12:]
    except Exception:
        references = 'references_'
    





    # name of local file
    '''
    local_file = 'local_copy.pdf'

    # Download remote and save locally

    try:
        urllib.request.urlretrieve(pdf_url, local_file)
    except Exception as e:
        print('Site arxiv does not provide access to pdf files')
        print(e.__class__, "occurred.")
        print('Let us try to use local_copy.pdf file')
        print('If no result below, upload local_copy.pdf file')

    '''
    # else:
        # try:
            # path_to_pdf = 'local_copy.pdf'
        # except Exception as e:
            # print(e.__class__, "occurred.")
            # print('File local_copy.pdf not found. Please, upload local_copy.pdf file')

    '''
    finally:
        # had an error: a bytes-like object is required, not 'str'
        # so added try
        try:
            text = extract_text(local_file)
            # 
            #
            #
            # text = send_a_pdf_to_api_and_get_text_from_api(pdf_url)
            #
            #
            #
            reference_word = 'Reference'
            # print(text.find(reference_word))
            # print(text[text.find(reference_word):)

            # get text of all references
            references = text[text.find(reference_word):]
            
            # to exclude the work references itself
            # return references[12:]
        except Exception:
            references = 'references_'
        
    '''
    return references[12:]



#
#
#

def get_array_of_references_from_string_of_references(references_2):
    array_of_references = []
    # sometimes read quality is bad, if many references are of bad quality, it skips the document
    max_numer_of_trials_to_read_reference = 30
    # j number of trials to read the file
    j = 0

    # if less than 10 characters left, it's not a complete reference
    while len(references_2)>10:
        ref_buffer = {}
        array_ref_authors = []

        ref_authors_end_index = references_2.find('(')
        
        ref_authors = references_2[:ref_authors_end_index]
        
        # keep text from right to the last new line symbol (\n)
        # in case line offset
        if ref_authors.rfind('\n') > 0:
            ref_authors = ref_authors[ref_authors.rfind('\n')+1:]
        
        # if there's no "." in authors field, it's wrong
        # if not ref_authors.find('.') == -1:
        #   continue

        array_ref_authors = line_of_authors_to_array(ref_authors)

        #array_ref_authors.append(ref_authors)
        ref_buffer['authors'] = array_ref_authors
        # print(ref_authors)

        date_end_index =  references_2.find(')')
        ref_year = references_2[ref_authors_end_index+1:date_end_index]

        # check line quality
        # and exit cycle if bad
        # used to verify if data is in 19** format
        date_format = '(^[1][9][0-9][0-9]$)'
        match = re.search(date_format, ref_year)
        # boolean = bool(match)
        if (not bool(match)) and (j<max_numer_of_trials_to_read_reference):
            references_2 = references_2[date_end_index+1:]
            j += 1
            # break
            continue

        ref_buffer['year'] = ref_year
        references_2 = references_2[date_end_index:]

        ref_title_start = references_2.find('.')
        # references_2[ref_title_end:]
        ref_title_end = references_2.find('.', references_2.find('.') + 1)
        ref_title = references_2[ref_title_start+2:ref_title_end].replace('\n', '')

        # REMPLACING UNACCEPTABLE FOR XML FORMAT CHARACTERS 
        #
        #
        ref_title = ref_title.replace('|', '_')
        ref_title = ref_title.replace("`", '_')
        ref_title = ref_title.replace('\\', '_')
        ref_title = ref_title.replace('"', '_')
        ref_title = ref_title.replace('{', '_')
        ref_title = ref_title.replace('}', '_')
        ref_title = ref_title.replace('(cid:14)', 'ffi')
        ref_title = ref_title.replace('(cid:12)', 'fi')
        ref_title = ref_title.replace('(cid:11)', 'ff')
        ref_title = ref_title.replace('(cid:13)', 'fl')
        ref_title = ref_title.replace('(unpublished)', '_')
        #
        #
        # 

        # print(ref_title)
        ref_buffer['title'] = ref_title
        references_2 = references_2[ref_title_end+2:]

        # ref_source = references_2[:references_2.find(',')].rstrip('\n')
        ref_source = references_2[:references_2.find(',')].replace('\n', '')
        
        references_2 = references_2[references_2.find('.')+3:]
        # print(ref_source)
        ref_buffer['ref_source'] = ref_source

        # if no "." there's no author, don't keep the whole line
        # if (ref_buffer) and ref_buffer['authors'] and (not ref_buffer['authors'][0].find('.') == -1):
        if (ref_buffer) and ref_buffer['authors'] and (not ref_buffer['authors'][0].find('.') == -1) and bool(re.search(date_format, ref_year)):
            array_of_references.append(ref_buffer)
    return array_of_references



#
# CREATES ONTO
#

def create_onto_from_one_article(article, array_of_references):
    ontology_local_link = 'onto_output.owl'
    onto = get_ontology("http://test.org/onto.owl")
    with onto:    
        class Authors(Thing):
            pass
        class Articles(Thing):
            pass
        class Journals(Thing):
            pass
        class Institutions(Thing):
            pass

        class wrote_article(ObjectProperty):
            domain = [Authors]
            range = [Articles]
        class works_in(ObjectProperty):
            domain = [Authors]
            range = [Institutions]
        class published_in(ObjectProperty):
            domain = [Authors]
            range = [Journals]
        class references_article(ObjectProperty):
            domain = [Articles]
            range = [Articles]
        class read_article(ObjectProperty):
            domain = [Authors]
            range = [Articles]
        class published_on_date(DataProperty):
            range = [str]

    # get data from article-dictionary
    authors = article['authors']
    
    published_on_date = article['published_on_date'].replace(' ', '_')

    article_title = article['title'].replace(' ', '_')
    article_i = Articles(article_title)

    journal_title = article['journal_ref'].replace(' ', '_')
    journal_i = Journals(journal_title)
    journal_i.published_on_date.append(published_on_date)
    

    for reference in array_of_references:
        # we search for article titles and replace spaces with underscore for better ontology representation
        # by underscore symbol for ontology representation      
        reference_title = reference['title']
        reference_title = reference_title.replace('  ', '_')
        reference_title = reference_title.replace(' ', '_')
    
        reference_i = Articles(reference_title)
        article_i.references_article.append(reference_i)
        
        

        for author_of_reference in reference['authors']:
            author_of_reference = author_of_reference.replace(' ', '_')
            # replace space by _ for otology representation
            # print(author_text)
            author_i = Authors(author_of_reference)
            author_i.wrote_article.append(article_i)

    for author in authors:

        author_i = Authors(author['name'].replace(' ', '_'))
        author_i.published_in.append(journal_i)
        author_i.wrote_article.append(article_i)

        try:
            lab_i = Institutions(author['lab'].replace(' ', '_'))    
            # print(lab_i)    
            author_i.works_in.append(lab_i)
            
        except Exception:
            pass
        
    onto.save(file = ontology_local_link)



#
# establishing connection with api
#

def send_a_pdf_to_api_and_get_text_from_api(file_url):
    local_file = 'local_copy.pdf'
    # it's the internal api 
    # is used to send pdf-file and get document_id
    post_url = "http://localhost:5000/documents"

    
    
    urllib.request.urlretrieve(file_url, local_file)
    
    files = {"file": open(local_file, "rb")}

    # send file
    response = requests.post(post_url, files=files)
    
    # api is configured to return documenet_id
    # get id of the document saved in database
    document_id = response.json()['id']

    # getting data from api
    get_url = "http://localhost:5000/text/"+str(document_id)+".txt"

    # the api is configured to return text when document_id is sent
    response = requests.get(get_url)
    # print(response.text['text'])
    text_from_file = response.json()

    return text_from_file['text']




#
# MAIN
#

def main():
    # request to arxiv
    url = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=1000'
    array_of_articles = get_article_data(url) # request to arxiv

    # onto file name
    # ontology_local_link = "owlready_onto_i.owl"

    # show list of dict of found articles
    '''
    for i in range(len(array_of_articles)):
        print(array_of_articles[i])
    '''

    # CYCLE THROUGH articles
    # we can extract much more from array of articles
    i = 0
    for article in array_of_articles:
        
        pdf_url = article['pdf_link']
        # references as result
        text = get_references_in_text_format_from_link(pdf_url)
        
        # text as result
        # text = send_a_pdf_to_api_and_get_text_from_api(pdf_url)
        
        array_of_references = get_array_of_references_from_string_of_references(text)
        # print(article)
        create_onto_from_one_article(article, array_of_references)
        i += 1
        print(i, pdf_url)
        # time.sleep(10)
    
    '''
    for article in array_of_articles:
        try:
            # go through articles and get its links
            # CREATE FNC THAT PUT ALL IN ONTO! 
            pdf_url = article['pdf_link']
            # extract text, specifically references in form of text
            text = get_references_in_text_format_from_link(pdf_url)
            array_of_references = get_array_of_references_from_string_of_references(text)

            for i in range(len(array_of_references)):
                print(array_of_references[i])
            
        except Exception as e:
            print(e.__class__, "occurred.")
    '''




if __name__ == "__main__":
    main()
