# -*- coding: utf-8 -*-

import requests
import sys
from bs4 import BeautifulSoup

start_url_list = ['http://invest.ppdai.com/loan/list_safe', 'http://invest.ppdai.com/loan/list_payfor', 'http://invest.ppdai.com/loan/list_riskmiddle',
					'http://invest.ppdai.com/loan/list_riskhigh', 'http://invest.ppdai.com/loan/list_bd​']
page_range = [(1, 3), (1, 46), (1, 10), (1, 46), (1, 2)]

request_params = {	'Connection': 'keep-alive',
					'Cache-Control': 'max-age=0',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
					'Accept-Encoding': 'gzip, deflate, sdch',
					'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
				}

def unique(items):
    keep = []
    for item in items:
        if item not in keep:
            keep.append(item)
    return keep

def do_request(url):
	while True:
		try:
			r = requests.get(url, headers = request_params, timeout = 10)
			if r.status_code != 200:
				print ("Http request error: " + str(r.status_code) + " ---- " + url)
				return ""
			return r.content
		except Exception:
			continue

def parse_load_list_page(url):
	html_content = do_request(url)
	if html_content == "":
		return []
	soup = BeautifulSoup(html_content)
	ret = []

	p = soup.find_all(name = 'p', class_ = 'userInfo clearfix')
	for item in p:
		ret.append(item.find(name = 'a')['href'])

	return ret

def parse_user_page(url):
	html_content = do_request(url)
	if html_content == "":
		return []
	soup = BeautifulSoup(html_content)
	ret_info = []
	user_info = []

	# Get user information
	li = soup.find(name = 'li', class_ = 'honor_li')
	span = li.find_all(name = 'span', class_ = 'cf7971a')
	for item in span:
		user_info.append(item.text)

	li = soup.find(name = 'li', class_ = 'user_li')
	span = li.find_all(name = 'span')
	user_info.append(span[0].text)

	# Get load urls
	div = soup.find_all(name = 'div', class_ = 'rightlist fl')
	for items in div:
		if items.text.find('100%') == -1:
			continue
		host = 'http://www.ppdai.com'
		s_url = host + items.find(name = 'a')['href']
		ret_info.append(parse_load_single_page(s_url, user_info))

	return ret_info

def parse_load_single_page(url, info):
	html_content = do_request(url)
	if html_content == "":
		return []
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
	ret_info = ret_info + info

	# 历史成功次数，历史流标次数
	div = soup.find(name = 'div', class_ = 'lendDetailContent_infoDetail_userInfo clearfix')
	p = div.find(name = 'p')
	span = p.find_all(name = 'span')
	ret_info.append(span[0].text)
	ret_info.append(span[1].text)

	# 借款进度
	div = soup.find_all(name = 'div', class_ = 'item')
	ret_info.append(div[1].text)

	# 投标数
	a = soup.find_all(name = 'a', class_ = 'listname')
	ret_info.append(str(len(a)))

	# 信用等级
	span = soup.find(name = 'span', title = '反映列表安全等级，等级越高逾期率越低')
	ret_info.append(span['class'][1])

	return ret_info

def output_to_file(file, info):
	for item in info:
		file.write(item.replace('\n', '').replace('\r', '').replace(' ', '') + ", ")
	file.write('\n')

def main():
	# Open data file in append mode
	if len(sys.argv) < 2:
		print ("Please specify output file name")
		return
	file_name = sys.argv[1]
	data_file = open(file_name, encoding = 'utf-8', mode = 'a')
	user_url_list = []

	s_len = len(start_url_list)
	for i in range(s_len):
		start_url = start_url_list[i]
		for page in range(page_range[i][0], page_range[i][1]):
			page_url = start_url + "_s0_p" + str(page)
			ret_user = parse_load_list_page(page_url)
			user_url_list = user_url_list + ret_user
			# print ('Parsing page: ' + page_url + '......')
			# res = parse_load_list_page(page_url)
			# if len(res) == 0:
			# 	break
			# for item in res:
			# 	info = parse_load_single_page(item)
			# 	if info[9].find('100%') != -1:
			# 		output_to_file(data_file, info)
			# 	handled_page_url.append(item)
			# print ('Finish page: ' + page_url) 
			# page = page + 1

	# Remove duplicated user urls
	user_url_list = unique(user_url_list)

	for item in user_url_list:
		print ('Parsing user: ' + item)
		info_list = parse_user_page(item)
		for info in info_list:
			output_to_file(data_file, info)
		print (str(len(info_list)) + " items added")

if __name__ == '__main__':
	main()