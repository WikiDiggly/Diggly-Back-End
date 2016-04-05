import string

from diggly.util.text_processor.text_process import Text_Process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text_proc = Text_Process()
token_dict = {}

def score_topics(source_id, topics_desc_dict):
    for tid, text in topics_desc_dict.iteritems():
        lowers = text.lower()
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        no_punctuation = lowers.translate(remove_punctuation_map)
        token_dict[tid] = no_punctuation

    print "\nTOKEN_DICT (in score_topics):\n"
    for a,b in token_dict.iteritems():
        print a, "\n"

    index = 0
    indices = {}
    res_dict = {}

    for tok in token_dict.keys():
        indices.update({tok: index})
        index += 1

    main_index = indices[source_id]

    # this can take some time
    tf_idf = TfidfVectorizer(tokenizer=text_proc.tokenize, stop_words='english')
    tfidf_matrix = tf_idf.fit_transform(token_dict.values())
    res = cosine_similarity(tfidf_matrix[main_index], tfidf_matrix)

    #print "INDEX -->", main_index, "\n"
    #print "TFS RES -->", res[0], "\n"
    #print "TFS MAIN_FIELDS -->", res[0][main_index], "\n"

    for tok,ind in indices.iteritems():
        res_dict.update({tok: res[0][ind]})

    return res_dict
