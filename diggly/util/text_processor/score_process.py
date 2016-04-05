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

    index = token_dict.keys().index(source_id)

    # this can take some time
    tf_idf = TfidfVectorizer(tokenizer=text_proc.tokenize, stop_words='english')
    tfidf_matrix = tf_idf.fit_transform(token_dict.values())
    res = cosine_similarity(tfidf_matrix[index], tfidf_matrix)

    print "INDEX -->", index, "\n"
    print "tfidf_matrix -->", vars(tfidf_matrix), "\n"
    print "TFS RES -->", res, "\n"
    return res
