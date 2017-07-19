
import random
import requests
from bs4 import BeautifulSoup
import re
from collections import deque
import time
import os

# 定义连接相关的内容
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
headers = {
	'user-agent': user_agent
}

# 起始爬取地址
start_url = "http://car.autohome.com.cn/shuyu"
last_visit = "http://car.autohome.com.cn/shuyu"
# 内容页模式和列表页模式
link = re.compile(r'(?<=href=")/shuyu/detail[_\d]+.html(?=">)')
pager = re.compile(r'(?<=href=")/shuyu/list[_\d]+.html(?=" >)')

pagers = deque()
links = deque()
seen = set()

pagers.append(start_url)


def visit_autohome(url, last):
	text = list()
	html = requests.get(url, headers={'user-agent': user_agent, 'referer': last}).text
	soup = BeautifulSoup(html, 'lxml')
	# 标题抽取
	title = soup.find('title').text.strip()
	text.append("title: {}".format(title))
	text.append("url: {}".format(url))

	print('开始收集于{}：\t{}'.format(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))), url))
	# print(title)
	nav = soup.find('div', class_="subnav overflow").find_all('a')
	nav = '>'.join(map(lambda x: x.text, nav))
	text.append('nav: {}'.format(nav))

	article = soup.find('div', class_='conleft').find_all('p')
	paragraphs = map(lambda x: x.text.replace('\xa0', ''), article)
	text.extend(paragraphs)

	output_file_name = './爬取结果/{}.txt'.format(title.replace(r"/","_"))
	if len(title)>40:
		output_file_name = './爬取结果/{}.txt'.format(title.replace(r"/","_")[40:]+"_Bysplit")
	if os.path.exists(output_file_name):
		return
	f = open(output_file_name, 'wt', encoding='utf-8')
	for i in text:
		f.write('{}{}'.format(i, '\n'))
	f.close()

def LoadUrls(path):
	lines = open(path, 'r',encoding='utf8')
	urls = set([i.replace('\n','') for i in lines])
	lines.close()
	return urls

url_path = "./urls.txt"
urls = LoadUrls(url_path)
append_urls = open(url_path,'a',encoding='utf8')
count = 0
print(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
while pagers:
	current_page = pagers.popleft()
	response = requests.get(current_page, headers=headers)
	current_html = response.text
	pagers_found = set(pager.findall(current_html))
	links_found = set(link.findall(current_html))
	pagers.extend(map(lambda x: 'http://car.autohome.com.cn' + x, pagers_found))
	links.extend(map(lambda x: 'http://car.autohome.com.cn' + x, links_found))

	while links:
		time.sleep(random.uniform(1,5))
		current_link = links.popleft()
		if not current_link in seen and not current_link in urls:
			visit_autohome(current_link, last_visit)
			seen.add(current_link)
			last_visit = current_link
			append_urls.write(current_link+'\n')
			append_urls.flush()
			count +=1
	seen.add(current_page)
	if count > 20:
		hour = 0
		min = random.uniform(1, 3)
		sec = random.uniform(1,59)
		second = hour*3600 + min*60 + sec
		time.sleep(second)
append_urls.close()
