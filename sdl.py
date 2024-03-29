#!/usr/bin/env python3
import argparse
import json
from lxml import etree
import os
import re
import requests
import sys

SERVERS = {
	'': '{}.wikisource.org',
	'mul': 'wikisource.org',
}

URLS = {
	'imageinfo': 'https://{}/w/api.php?format=json&action=query&titles=File:{}&prop=imageinfo&iiprop=size',
	'export_titles': 'https://{}/w/api.php?format=json&action=query&export=true&titles={}'
}

API_PAGE_LIMIT = 50

REQUESTS_HEADERS = {
	'User-Agent': 'https://github.com/szc126/sdl',
}

def server(lang):
	return lang in SERVERS and SERVERS[lang] or SERVERS[''].format(lang)

def generate_sessions(title, pagecount):
	sessions = []
	range_start = 1
	range_stop = min(pagecount, API_PAGE_LIMIT) # do not download 50 pages if there are 8 pages
	while range_start < pagecount:
		session = []
		for i in range(range_start, range_stop + 1):
			session.append(f'Page:{title}/{i}')
		range_start += API_PAGE_LIMIT
		range_stop = min(pagecount, range_stop + API_PAGE_LIMIT)
		sessions.append(session)
	return sessions

def query_imageinfo(lang, title):
	url = URLS['imageinfo'].format(server(lang), title)
	content = requests.get(url, headers = REQUESTS_HEADERS).content

	print(url)
	print('response size: ' + str(len(content)))
	return json.loads(content)

def query_export_titles(lang, session):
	url = URLS['export_titles'].format(server(lang), '|'.join(session))
	content = requests.get(url, headers = REQUESTS_HEADERS).content

	print(url)
	print('response size: ' + str(len(content)))
	return json.loads(content)

def main(args):
	_ = args.book.split(':')
	lang, title = _[0], _[1].replace(' ', '_')
	print(f'{title} at {lang}.ws')
	print()

	print('(downloading info)')
	imageinfo = query_imageinfo(lang, title)
	try:
		pagecount = imageinfo['query']['pages']['-1']['imageinfo'][0]['pagecount']
		print(f'pagecount: {pagecount} pages')
	except:
		sys.exit('pagecount: n/a; exiting')
	if args.D: input('... [artichoke]')
	print()

	print('(downloading export)')
	sessions = generate_sessions(title, pagecount)
	exports = []
	for session in sessions:
		exports.append(query_export_titles(lang, session))
	if args.D: input('... [carrot]')
	print()

	print('(collecting pages)')
	pages = []
	for export in exports:
		export = export['query']['export']['*']
		export = etree.fromstring(export)
		for child in export.findall('{*}page'): # `{*}`: wildcard (`*`) XML namespace (`{}`)
			#print(etree.tostring(child))
			#print()
			title = child.find('{*}title')
			text = child.find('{*}revision/{*}text')
			pages.append({
				'title': title is not None and title.text,
				'text': text is not None and text.text,
			})
	if args.D: input('... [cabbage]')
	print()

	if args.D:
		print('(printing pages)')
		for page in pages:
			print(page['title'])
			print(page['text'])
			print()
		if args.D: input('... [ungchoy]')
		print()

	if args.out_dir:
		print('(making output directory. will overwrite existing files!)')
		if not os.path.exists(args.out_dir):
			os.makedirs(args.out_dir)
		if args.D: input('... [cilantro]')
		print()

		print('(writing to disk)')
		for page in pages:
			filename = re.sub(r'.+/(\d)', r'\1', page['title']) # XXX: localization?
			path = os.path.join(args.out_dir, filename)
			if args.D: print(path)
			with open(path, mode = 'w', encoding = 'utf-8') as file:
				file.write(page['text'])
		if args.D: input('... [bo choy]')
		print()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'book',
		metavar = 'lang:file',
	)
	parser.add_argument(
		'-o',
		dest = 'out_dir',
		metavar = 'directory',
		help = 'output directory',
	)
	parser.add_argument(
		'-D',
		action = 'store_true',
		help = 'debug',
	)
	args = parser.parse_args()

	main(args)
