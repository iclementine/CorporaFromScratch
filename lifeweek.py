#!/usr/bin/python3
# 这是一个打算抓取三联生活周刊的练习的方案，需要涉及到各种肮脏的事情啦

import urllib.request
import re
from collections import deque
from bs4 import BeautifulSoup

# 这是三联生活周刊的文化版面的起始
start_url = 'http://app.lifeweek.com.cn/?app=article&controller=allarticle&catid=6&page=30'
# 根据一种认识，这样子的才是页面正文，另外的样子就是翻页器
link = re.compile(r'(?<=href=")(http://www.lifeweek.com.cn/\d{4}/\d{4}/\d+.shtml)(?=")')
pager = re.compile(r'(?<=href=")(http://app.lifeweek.com.cn/\?app=article&controller=allarticle&catid=6&page=\d+)(?=")')


pagers = deque()
links = deque()
seen = set()

pagers.append(start_url)

def next_page(url):
	if not re.match(r'_\d+.shtml$', url):
		return re.sub(r'.shtml$', '_2.shtml', url)
	else:
		p = int(re.search(r'(?<=_)(\d)(?=\.shtml$)', url).group(1))+1
		return re.sub(r'(?<=_)(\d)(?=\.shtml$)', str(p), url)

def visit_lifeweek(url):
	text = list()
	html = urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf8')	
	soup = BeautifulSoup(html, 'lxml')
	title = soup.find('title').text
	text.append(title)
	print('{}：开始收集于：\n\t{}'.format(title,url))
	article = soup.find('article').findAll('p')
	paragraphs = map(lambda x:x.text.replace('\xa0', ''), article)
	text.extend(paragraphs)
	try:
		html = urllib.request.urlopen(urllib.request.Request(next_page(url))).read().decode('utf8')	
		soup = BeautifulSoup(html, 'lxml')
		try:
			article = soup.find('article').findAll('p')
			paragraphs = map(lambda x:x.text.replace('\xa0', ''), article)
			text.extend(paragraphs)
		except:
			print('{}{}'.format(title, '这一页没有内容了'))
	except urllib.request.HTTPError as e:
		print('{}：{}：收集完成'.format(e.code, title))
		pass
	f = open('./文化版/{}.txt'.format(title), 'wt')
	for i in text:
		f.write('{}{}'.format(i, '\n'))
	f.close()
	
while pagers:
	current_page = pagers.popleft()
	current_html = urllib.request.urlopen(urllib.request.Request(current_page)).read().decode('utf8')
	pagers.extend(pager.findall(current_html))
	links.extend(link.findall(current_html))
	while links:
		current_link = links.popleft()
		if not current_link in seen:
			visit_lifeweek(current_link)
			seen.add(current_link)
	seen.add(current_page)
