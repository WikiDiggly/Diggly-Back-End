# 2016 wikidiggly

# base urls for wikipedia api, see https://en.wikipedia.org/w/api.php?action=help&modules=main
PAGE_INFO_URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&{}"
EXTRACT_URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&redirects&explaintext=&{}"
PARSE_URL = "https://en.wikipedia.org/w/api.php?action=parse&prop=sections|links&contentformat=text/plain&pageid={}"
LINKED_TOPICS_URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=max&plnamespace=0&{}"
SECTIONS_URL = "https://en.wikipedia.org/w/api.php?action=parse&prop=sections"
REDIRECT_URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&redirects=&{}"
WIKI_URL_BASE = "https://en.wikipedia.org/wiki/{}"

RVCONT = "rvcontinue"
EXCONT = "excontinue"
PLCONT = "plcontinue"

EXINTRO = "&exintro="
EXSENTENCES = "&exsentences={}"
R_TITLE = "titles={}"
R_PAGEID = "pageids={}"
ARG_SEP = "|"
TITLE_SEP = "_"

PAGE_RESP_KEY = 'page_resp'
REDIRECT_RESP_KEY = 'redirect_resp'

DEFAULT_NUM_LINKED_TOPICS = 7
NUM_TOP_LINKS = 15
MAX_NUM_LINKED_TOPICS = 500
DEFAULT_DESC_LENGTH = 6
DEFAULT_SUMM_LENGTH = 2
MAX_NUM_THREADS = 8
