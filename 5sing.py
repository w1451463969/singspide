
from urllib.request import urlopen, ProxyHandler, build_opener
from bs4 import BeautifulSoup
import json
import pymysql
import threading
#SELECT * FROM `iplist` ORDER BY rand( ) LIMIT 1  随机抽取一条记录

lock = threading.Lock()
lockip = threading.Lock()

connip = pymysql.connect(host = '127.0.0.1',
						user = 'root',
						passwd = 'root',
						db = 'mysql', 
						charset = 'utf8',
						cursorclass=pymysql.cursors.DictCursor)

curip = connip.cursor()
curip.execute("use agentip")


conn = pymysql.connect(host = '127.0.0.1',
						user = 'root',
						passwd = 'root',
						db = 'mysql', 
						charset = 'utf8',
						cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

try:
	cur.execute("use 5SingSong")
except Exception as e:
	cur.execute("create database 5SingSong")
	cur.execute("use 5SingSong")
	cur.execute("create table song (id bigint(7) not null auto_increment, title varchar(200), renqi int, songid int, httpstate int, created timestamp default current_timestamp, primary key(id)) character set = utf8")

def store(title, renqi, songid,httpstate):
	try:
		lock.acquire()
		#print(type(songid))
		#print(type(title))
		#print(type(renqi))
		cur.execute("insert into song (title, renqi, songid, httpstate) values (\"%s\", \"%s\", \"%s\", \"%s\")", (title, renqi, songid, httpstate))
		conn.commit()
		lock.release()
	except Exception as e:
		lock.release()
		#raise e
		pass
		
def agentopener(ip, port):
	d = {'http': ''}
	d['http'] = 'http://' + ip.rstrip('\'').lstrip('\'') + ':' + port.rstrip('\'').lstrip('\'') + '/'
	print(d)
	proxy_support = ProxyHandler(d)
	opener = build_opener(proxy_support)
	return opener

def handle_html(songid,opener):
	try:	
		html = opener.open("http://5sing.kugou.com/yc/rq/"+str(songid))
		bsObj = BeautifulSoup(html, "html.parser")
		title = bsObj.find("head").find("title").get_text()
		print (title)
		#renqi = bsObj.find("div", {"class":"r_t"}).find("span").get_text()
		#js = urlopen("http://service.5sing.kugou.com/analysis/songGraph?jsoncallback=type=1&SongID="+str(songid)+"&SongType=yc")
		try:
			js = opener.open("http://service.5sing.kugou.com/analysis/songGraph?jsoncallback=type=1&SongID="+str(songid)+"&SongType=yc")
			strjs = js.read()
			strjs = strjs[7:]
			strjs = strjs[:-1]
			b = eval(strjs)
			#print(type(b['rq']))
			#print(type(title))
			#print(type(songid))
			store(title, b['rq'], songid, 200)
		except Exception as r:
			print(r)
			getLink(int(songid))

		

	except Exception as e:
		try:
			print (e)
			if e.code == 302:
				store("不存在", "rq", songid, 404)
			else:
				getLink(int(songid))
		except Exception as e:
			getLink(int(songid))



def getLink(songid):
	lockip.acquire()
	curip.execute("select* from `iplist` order by rand() limit 1")
	data = curip.fetchone()
	lockip.release()
	agent = agentopener(data['ip'],data['port'])
	t = threading.Thread(target = handle_html, args = (songid, agent))
	t.start()
	#handle_html(songid, agent) 

if __name__ == '__main__':	
	for x in range(1,9999):
		getLink(x)

