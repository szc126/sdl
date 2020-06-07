#!/usr/bin/env python3
import argparse
import json
from lxml import etree
import requests
import sys

URLS = {
	'imageinfo': 'https://{}.wikisource.org/w/api.php?format=json&action=query&titles=File:{}&prop=imageinfo&iiprop=size',
	'titles': 'https://{}.wikisource.org/w/api.php?format=json&action=query&export=true&titles={}'
}

API_PAGE_LIMIT = 50

def query_imageinfo(lang, title):
	url = URLS['imageinfo'].format(lang, title)
	content = requests.get(url).content

	print(url)
	print('response size: ' + str(len(content)))
	return json.loads(content)

def query_pages(lang, title, range_start, range_stop):
	titles = []
	for i in range(range_start, range_stop + 1):
		titles.append(f'Page:{title}/{i}')
	url = URLS['titles'].format(lang, '|'.join(titles))

	content = requests.get(url).content
	print(url)
	print('response size: ' + str(len(content)))
	return json.loads(content)

def main():
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
	input('... [artichoke]')
	print()

	print('(downloading export)')
	exports = []
	range_start = 1
	range_stop = min(pagecount, API_PAGE_LIMIT) # do not download 50 pages if there are 8 pages
	while range_start < pagecount:
		exports.append(query_pages(lang, title, range_start, range_stop))
		range_start += API_PAGE_LIMIT
		range_stop = min(pagecount, range_stop + API_PAGE_LIMIT)
		print()
	input('... [carrot]')
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
	input('... [cabbage]')
	print()

	print('(printing pages)')
	for page in pages:
		print(page['title'])
		print(page['text'])
		print()
	input('... [ungchoy]')
	print()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'book',
		metavar='lang:file',
	)
	args = parser.parse_args()

	main()
