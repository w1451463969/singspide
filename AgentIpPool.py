import requests
from urllib.request import urlopen, ProxyHandler, build_opener
from bs4 import BeautifulSoup
import time
import threading
import pymysql
from timeit import timeit



conn = pymysql.connect(host = '127.0.0.1',
						user = 'root',
						passwd = 'root',
						db = 'mysql', 
						charset = 'utf8',
						cursorclass = pymysql.cursors.DictCursor)
cur = conn.cursor()
try:
	cur.execute("use AgentIp")
except Exception as e:
	cur.execute("create database AgentIp")
	cur.execute("use AgentIp")
	cur.execute("create table ipList (ip varchar(20), port varchar(6), area varchar(20), primary key(ip)) character set = utf8")
	conn.commit()

mu = threading.Lock()
spidenumlist = []
spidenum = 0
def spide_url(url):
	try:
		
		headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
		html = requests.get(url, headers = headers).content
		#print(html)		
		bsObj = BeautifulSoup(html, "html.parser")
		ipList = bsObj.find("table", {"bordercolor":"#6699ff"}).find_all("tr")
		#print(ipList)
		for x in ipList:
			td = x.find_all("td")
			#print(td[0].get_text())
			#print(td[1].get_text())
			#print(td[2].get_text())
			ip = td[0].get_text()#ip地址
			port = td[1].get_text()#端口号
			area = td[2].get_text()#地区
			
			#check_agent(ip, port)
			if(ip!="ip"):
				
				t = threading.Thread(target = check_agent, args = (ip,port,area))
				spidenumlist.append(t)
				#spidenum = spidenum + 1

				t.start()
	except Exception as e:
		raise e
	

def check_agent(ip, port,area):
	#print("ip:",ip,"port:",port)
	d = {'http': ''}
	d['http'] = 'http://' + str(ip) + ':' + str(port) + '/'
	#print(d)
	proxy_support = ProxyHandler(d)
	opener = build_opener(proxy_support)
	try:
		if(opener.open("http://5sing.kugou.com/index.html").code == 200):
			try:
				#print("验证成功" + str(d))
				mu.acquire()
				cur.execute("insert into ipList (ip, port,area) values (\"%s\", \"%s\", \"%s\")", (ip, str(port), str(area)))
				conn.commit()
				print("插入成功"+ str(d))
				mu.release()
 
			except Exception as e:
				mu.release()
				pass
		else:
			#print("代理失效")
			pass
	except Exception as d:
		#print("代理失效")
		#mu.release()
		pass
	
def main():
	for area in range(1,35):
		for page in range(1,5):
			str_url = "http://www.66ip.cn/areaindex_"+str(area)+"/"+str(page)+".html"
			print("处理地区" +str(area)+ "第" + str(page) + "页中")
			time.sleep(2)
			spide_url(str_url)
	for x in spidenumlist:
		x.join()

if __name__ == '__main__':
	print("总耗时 ：" + str(timeit('main()', 'from __main__ import main', number=1)))
	print("代理爬取完毕")



