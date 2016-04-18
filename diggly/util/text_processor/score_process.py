import string

from diggly.util.text_processor.text_process import Text_Process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text_proc = Text_Process()

def score_topics(source_id, topics_desc_dict):
    token_dict = {}
    indices = {}
    res_dict = {}
    index = 0

    for tid, text in topics_desc_dict.iteritems():
        lowers = text.lower()
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        no_punctuation = lowers.translate(remove_punctuation_map)
        token_dict[tid] = no_punctuation

    for tok in token_dict.keys():
        indices.update({tok: index})
        index += 1

    main_index = indices[source_id]

    # this can take some time
    tf_idf = TfidfVectorizer(tokenizer=text_proc.tokenize, stop_words='english')
    tfidf_matrix = tf_idf.fit_transform(token_dict.values())
    res = cosine_similarity(tfidf_matrix[main_index], tfidf_matrix)

    for tok, ind in indices.iteritems():
        if tok == main_index:
            continue;
        res_dict.update({tok: res[0][ind]})

    return res_dict

def score_outlinks(main_text, title_list):
    main_title = "current_selected_topic"
    token_dict = {}
    len_titles = {}
    indices = {}
    res_dict = {}
    index = 0

    for title in title_list:
        lowers = title.lower().replace("_", " ").replace("-", " ")
        len_titles.update({title: len(lowers.split(" "))})
        token_dict[title] = lowers

    len_titles[main_title] = 1
    token_dict[main_title] = main_text

    for tok in token_dict.keys():
        indices.update({tok: index})
        index += 1

    main_index = indices[main_title]

    tf_idf = TfidfVectorizer(tokenizer=text_proc.tokenize, stop_words='english')
    tfidf_matrix = tf_idf.fit_transform(token_dict.values())
    res = cosine_similarity(tfidf_matrix[main_index], tfidf_matrix)

    for tok, ind in indices.iteritems():
        if tok == main_title:
            continue;
        res_dict.update({tok: (res[0][ind] * 100 / len_titles[tok]) })

    return res_dict



