# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

start_url_list = ['http://invest.ppdai.com/loan/list_safe', 'http://invest.ppdai.com/loan/list_payfor', 'http://invest.ppdai.com/loan/list_riskmiddle',
					'http://invest.ppdai.com/loan/list_riskhigh', 'http://invest.ppdai.com/loan/list_bd​']

request_params = {	'Connection': 'keep-alive',
					'Cache-Control': 'max-age=0',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
					'Accept-Encoding': 'gzip, deflate, sdch',
					'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
				}

def do_request(url):
	r = requests.get(url, headers = request_params, timeout = 10)
	if r.status_code != 200:
		print ("Http request error: " + str(r.status_code) + " ---- " + url)
		return ""
	return r.content

def parse_load_list_page(url):
	html_content = do_request(url)
	if html_content == "":
		return []
	soup = BeautifulSoup(html_content)
	ret = []

	load_list = soup.find_all(name = 'a', class_ = 'title ell')
	for item in load_list:
		ret.append(item['href'])

	return ret

def parse_user_page(url):
	html_content = do_request(url)
	soup = BeautifulSoup(html_content)
	ret = []

	li = soup.find(name = 'li', class_ = 'honor_li')
	span = li.find_all(name = 'span', class_ = 'cf7971a')
	for item in span:
		ret.append(item.text)

	li = soup.find(name = 'li', class_ = 'user_li')
	span = li.find_all(name = 'span')
	ret.append(span[0].text)

	return ret

def parse_load_single_page(url):
	html_content = do_request(url)
	soup = BeautifulSoup(html_content)
	ret_info = []

	# 借款总额，年利率，期限
	div = soup.find(name = 'div', class_ = 'w528 clearfix')
	dd = div.find_all(name = 'dd')
	for item in dd:
		ret_info.append(item.text)

	# 还款方式
	div = soup.find_all(name = 'div', class_ = 'item item1')
	ret_info.append(div[0].text)

	# 借入信用等级，借出信息等级，性别
	a = soup.find(name = 'a', class_ = 'username')
	user_info = parse_user_page(a['href'])
	ret_info = ret_info + user_info

	# 历史成功次数，历史流标次数
	div = soup.find(name = 'div', class_ = 'lendDetailContent_infoDetail_userInfo clearfix')
	p = div.find(name = 'p')
	span = p.find_all(name = 'span')
	ret_info.append(span[0].text)
	ret_info.append(span[1].text)

	# 借款进度
	div = soup.find_all(name = 'div', class_ = 'item')
	ret_info.append(div[1].text)

	return ret_info

def output_to_file(file, info_list):
	for item in info_list:
		file.write(item.replace('\n', '').replace('\r', '').replace(' ', '') + ", ")
	file.write('\n')

def main():
	# Open data file in append mode
	data_file = open('data.txt', encoding = 'utf-8', mode = 'a')

	for start_url in start_url_list:
		while True:
			page = 1
			page_url = start_url + "_s0_p" + str(page)
			res = parse_load_list_page(page_url)
			if len(res) == 0:
				continue
			for item in res:
				info = parse_load_single_page(item)
				output_to_file(data_file, info)
			print ("Finish page: " + page_url) 
			page = page + 1

if __name__ == '__main__':
	main()