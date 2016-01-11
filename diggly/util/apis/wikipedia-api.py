import sys
import os
import requests


# 2016 wikidiggly
# author: ola-halima
# prototype v1

base_url = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&formatversion=2&{}"
r_title = "title={}"
r_pageid = "pageids={}"
arg_seperator = "|"


def get_article( r_args ):
    resources = format_req(r_args)

    r_url = baseurl.format(resources)
    resp = requests.get(r_url)

    if resp.status_code != 200:
        #TODO: handle exception better
        raise ApiError('GET: article information\n{}'.format(resp.status_code))

    pages = resp.json()['pages']:

def parse_pages(pages):
    for page in pages:
        pid = page['pageid']
        title = page['title']
        
        pcontent = page["revisions"]['content'] 
        description = 

def format_req( r_args ):
    r_format = ""
    isStrings = False

    if is_seq(pids): # check if arg is a list
        if is_pageid(r_args[0]):
            return r_pageid.format(arg_separator.join(r_args))
        else:
            return r.title.format(arg_separator.join(r_args))
    
    if is_pageid(r_args):
        return r.pageid.format(r_args)

    #default return single page title format
    return r.title.format(r_args)

def is_pageid(arg):
    try:
        pid = int(arg)
        return True;
    
    except ValueError:
        return False;    

def is_seq(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
