import requests
import bs4
import re
import MySQLdb
import time
import os
import tplink
import sys
import traceback

def soup(url):
    temp = s.get(url)
    if temp.status_code ==200:
        soup1 = bs4.BeautifulSoup(temp.text,'html.parser')
        return soup1
    else:
        print('ip gg2','\033[34m%s\033[0m'%time.ctime())
        

def restart(p,try_times):
    os.system('taskkill /F /IM  SangforCSClient.exe')
    time.sleep(30)
    os.system('taskkill /F /IM EasyConnect.exe')
    time.sleep(40)
    os.popen('"C:\\Program Files (x86)\\Sangfor\\SSL\\EasyConnect\\EasyConnect.exe"')
    time.sleep(60)
    try_times+=1
    p+=1
    return p,try_times


db = MySQLdb.connect('localhost','root','dpenger','douban',charset = 'utf8mb4')
cursor = db.cursor()


s = requests.Session()
headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
s.headers.update(headers)

#获取数据库中已有数据
sql1 = 'select * from post;'
cursor.execute(sql1)
results = cursor.fetchall()
exists = []
for result in results:
    exists.append(result[0])

#重连vpn计数
try_times = 0



#获取豆瓣一页中帖子url
#p = 1748
p=1
while p < 10000:
    try:
        #把每页的帖子整合到url_tuple中
        url_tuple = []
        group_url = 'https://www.douban.com/group/586674/discussion?start=%d'%(p*25)
        
        soup_group =soup(group_url)
    
        group_lists = soup_group.find(class_='olt').contents[2:]
        
        for each_url in group_lists:
            if each_url != '\n':
                url_tuple.append(each_url.td.a['href'])
        
        #检查该页中帖子是否已经存储在数据库中
        #如果为否，则进行爬取，如果为是，则跳过
        for url in url_tuple:
            if int(re.search('\d+',url).group()) in exists:
                continue
            i = 1
            r = s.get(url)
            if r.status_code !=200:
                #ip被封，换
                print('ip gg3')
                print(url,p,'\033[34m%s\033[0m'%time.ctime())
                try_times+=1
                p+=1
                net = tplink.tplink()
                if net == 1:
                    break
                #重新设置session
                s = requests.Session()
                s.headers.update(headers)
                continue
            
            
            soup_post = bs4.BeautifulSoup(r.text,'html.parser')
            try:
                floors_num = (len(soup_post.find(id='comments'))-1)/2
            except TypeError as e:
                if e.args[0] == "object of type 'NoneType' has no len()":
                    print(url,'无评论',time.ctime(),r.status_code)
                    continue
                print('ip gg1','\033[34m%s\033[0m'%time.ctime())
                try_times+=1
                p+=1
                net_sub=tplink.tplink()
                if net_sub == 1:
                    break
                continue
            except Exception as e:
                print(url,e,'无评论',time.ctime())
                continue
            if floors_num ==100:
                try:
                    total_page = int(soup_post.find(class_='thispage')['data-total-page'])
                except Exception as e:
                    total_page = 1
                    print(url,e,'评论刚好100',time.ctime(),r.status_code)       
            else :
                total_page = 1
            post_url = re.search('\d+',url).group()
            post_title = soup_post.find(class_='article').h1.text.replace('\n','').replace(' ','')[:40]
            try:
                post_content = soup_post.find(class_='topic-richtext').text[:1000]
            except Exception :
                post_content = soup_post.find(class_='topic-content').text[:1000]
#                print(post_url,'过去较久发的帖子')
            post_id = soup_post.find(class_='from').a.text[:20]
            post_id_url_eng = ''
            try:
                post_id_url = re.search('\d+',soup_post.find(class_='from').a['href']).group()
                if int(post_id_url) >2147483647:
                    post_id_url = 0
                    post_id_url_eng = re.search('/people/(.+?)/',soup_post.find(class_='from').a['href']).group(1)
                    
            except Exception as e:
                post_id_url = 0
#                print(post_url,'id_url为英文')
                post_id_url_eng = re.search('/people/(.+?)/',soup_post.find(class_='from').a['href']).group(1)[:30]
            
            
            #加入数据库主表
    #        sql_post = 'INSERT INTO post VALUES (%s,"%s","%s","%s",%s)',(post_url,post_title,post_content,post_id,post_id_url)
    #        cursor.execute(sql_post)
            if post_url in exists:
                continue
            cursor.execute('INSERT INTO post VALUES (%s,%s,%s,%s,%s,%s)',(post_url,post_title,post_content,post_id,post_id_url,post_id_url_eng))
            exists.append(int(post_url))
            soup_page = soup_post
            #副表
            while total_page >= i:
            
                floors_contents = soup_page.find(id='comments').contents
                for floor in floors_contents:
                    if floor !='\n':
                        reply_id =  floor.h4.a.text[:20]
                        reply_id_url = floor['data-author-id']
                        reply_content = floor.find(class_='reply-content').text[:1000]  
                        reply_id_url_eng = re.search('/people/(.+?)/',floor.find(class_='bg-img-green').a['href']).group(1)[:30]
                        
                        if reply_id_url_eng == reply_id_url:
                            reply_id_url_eng = ''
                        reply_time = floor.h4.span.text 
                            
                        pages = i
                        #逐个加入数据库副表
                        cursor.execute('INSERT INTO reply VALUES (%s,%s,%s,%s,%s,%s,%s)',(reply_id,reply_id_url,reply_content,post_url,pages,reply_id_url_eng,reply_time))
    
                if total_page!=1:
                    url_page = 'https://www.douban.com/group/topic/%s/?start=%d00'%(post_url,i)
                    rr = s.get(url_page)
                    soup_page = bs4.BeautifulSoup(rr.text,'html.parser')
                i+=1
            
            db.commit()
            
        p+=1
    except AttributeError as e:
        print(e,'ip gg','\033[34m%s\033[0m'%time.ctime())
        print(p)
        if try_times>=1:
            break
#        p,try_times = restart(p,try_times)
        try_times+=1
        p+=1
        net = tplink.tplink()
        if net == 1:
            break
        #重新设置session
        s = requests.Session()
        s.headers.update(headers)
        continue
#        break
    except requests.adapters.ConnectionError as e:
        print(e,'停十秒试试')
        a,b,c = sys.exc_info()
        print(traceback.extract_tb(c))
        s = requests.Session()
        s.headers.update(headers)
        time.sleep(10)
        continue
    except Exception as e:
        print(e)
        print(type(e))
        print('未知错误')
        a,b,c = sys.exc_info()
        print(traceback.extract_tb(c))
        print('p值为：',p)
        break

    
sql1 = 'select * from post;'
cursor.execute(sql1)
results = cursor.fetchall()
sql1 = 'select * from reply;'
cursor.execute(sql1)
results1 = cursor.fetchall()
#
#
#db.commit()

sql2 = 'select * from reply where reply_id_url = 205376874;'
cursor.execute(sql2)
results2 = cursor.fetchall()


sql3 = 'select * from post where post_id_url = 205376874;'
cursor.execute(sql3)
results3 = cursor.fetchall()

sql4 = 'select post.post_url,reply_content,post_title,post_content,reply_time from reply,post where post.post_url=reply.post_url and reply_id_url = 205376874;'
cursor.execute(sql4)
results4 = cursor.fetchall()

print('done!')
cursor.close()
db.close()
#建表
#帖子网址-主键post_url
#帖子标题post_title
#内容VARCHAR post_content
#发帖用户id post_id
#发帖用户主页网址 post_id_url
#发帖用户主页英文网址post_id_url_eng只有较早注册的用户才有
#
#回帖用户id reply_id
#回帖用户主页网址 reply_id_url
#回帖内容 reply_content
#回帖记号 post_url 外键至帖子网址post_url
#回帖用户主页英文网址reply_id_url_eng
#
#cursor.close()
#db.close()

