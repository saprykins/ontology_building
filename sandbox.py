from owlready2 import *

ontology_local_link = "owlready_onto_i.owl"
# ontology_local_link_output = "owlready_onto_o.owl"

def create_onto(article):
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
        class referenced(ObjectProperty):
            domain = [Authors]
            range = [Articles]
        class works_in(ObjectProperty):
            domain = [Authors]
            range = [Institutions]
        class published_in(ObjectProperty):
            domain = [Authors]
            range = [Journals]

    # get data from article-dictionary
    authors = article['authors']
    
    article_title = article['title'].replace(' ', '_')
    article_i = Articles(article_title)

    journal_title = article['journal_ref'].replace(' ', '_')
    journal_i = Journals(journal_title)
    
    for author in authors:
        author_i = Authors(author['name'].replace(' ', '_'))
        lab_i = Authors(author['lab'].replace(' ', '_'))
        # print(lab_i)
        author_i.wrote_article.append(article_i)
        author_i.works_in.append(lab_i)
        author_i.published_in.append(journal_i)
        author_i.wrote_article.append(article_i)

    onto.save(file = ontology_local_link)
    # onto.save()



article = {'pdf_link': 'http://arxiv.org/pdf/cond-mat/0102536v1', 'authors': [{'name': 'David Prendergast', 'lab': 'Department of Physics'}, {'name': 'M. Nolan', 'lab': 'NMRC, University College, Cork, Ireland'}, {'name': 'Claudia Filippi', 'lab': 'Department of Physics'}, {'name': 'Stephen Fahy', 'lab': 'Department of Physics'}, {'name': 'J. C. Greer', 'lab': 'NMRC, University College, Cork, Ireland'}], 'published': '2001-02-28T20:12:09Z', 'title': 'Impact of Electron-Electron Cusp on Configuration Interaction Energies', 'summary': '  The effect of the electron-electron cusp on the convergence of configuration\ninteraction (CI) wave functions is examined. By analogy with the\npseudopotential approach for electron-ion interactions, an effective\nelectron-electron interaction is developed which closely reproduces the\nscattering of the Coulomb interaction but is smooth and finite at zero\nelectron-electron separation. The exact many-electron wave function for this\nsmooth effective interaction has no cusp at zero electron-electron separation.\nWe perform CI and quantum Monte Carlo calculations for He and Be atoms, both\nwith the Coulomb electron-electron interaction and with the smooth effective\nelectron-electron interaction. We find that convergence of the CI expansion of\nthe wave function for the smooth electron-electron interaction is not\nsignificantly improved compared with that for the divergent Coulomb interaction\nfor energy differences on the order of 1 mHartree. This shows that, contrary to\npopular belief, description of the electron-electron cusp is not a limiting\nfactor, to within chemical accuracy, for CI calculations.\n', 'comment': '11 pages, 6 figures, 3 tables, LaTeX209, submitted to The Journal of\n  Chemical Physics', 'journal_ref': 'J. Chem. Phys. 115, 1626 (2001)'}
create_onto(article)
# translate_article_to_ontology(article)
