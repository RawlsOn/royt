from django.conf import settings
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()


from common.util.model_util import *

def add_search_keyword_em(search_text, data):
	if search_text is None or search_text.strip() == '': return data
	for datum in data:
		datum['content_html'] = _add_em(search_text, datum['content'])
	return data

def _add_em(search_text, content):
	splitted = search_text.split()
	for word in splitted:
		content = content.replace(word, f'<em>{word}</em>')
	return content