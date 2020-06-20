import requests
import bs4
import re

proxies = []
s = requests.Session()
headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        
                
        }
s.headers.update(headers)
r = s.get('https://www.kuaidaili.com/free/intr/1/')
soup = bs4.BeautifulSoup(r.text,'html.parser')
proxy_lists = soup.find(class_='table table-bordered table-striped').tbody.contents
for i in proxy_lists:
    if i == '\n':
        continue
    
    ip = i.find(attrs={'data-title':'IP'}).text
    port = i.find(attrs={'data-title':'PORT'}).text
    way = i.find(attrs={'data-title':'类型'}).text.lower()
    proxy = {
            way:'%s:%s'%(ip,port)
            }




    #r = s.get('https://baidu.com')
    try:
    #    r = s.get('https://baidu.com')
        r = s.get('http://httpbin.org/ip',proxies = proxy,timeout = 2)
    except requests.exceptions.ConnectTimeout as e:
        print('Invalid!')
    except requests.adapters.ReadTimeout as e:
        print(e)
        print(type(e))
        print('oops!')
    except Exception as e:
        print(type(e))
    else:
        proxies.append(proxy)
    finally:
        print('Done!')
        
        
#r = s.get('http://ip.tool.chinaz.com/',proxies ={'http': '119.57.156.90:53281'},timeout = 2)
#try:
#    1/0
#except ZeroDivisionError as e:
#    print(e)
#    print(type(e))
#else:
#    print('no problem')
#finally:
#    print('Done!')