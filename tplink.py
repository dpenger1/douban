import requests
import time
import os


def tplink():
    s = requests.Session()
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Host': '192.168.0.1',
    
    }
    
    s.headers.update(headers)
    s.get('http://192.168.0.1')
    
    headers1 = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'http://192.168.0.1',
            'Referer': 'http://192.168.0.1/',
            
            }
    
    s.headers.update(headers1)
    json_login = {"method":"do",
                  "login":{"password":"xlZgrJaUdTefbwK"}
                  }
    r0 = s.post('http://192.168.0.1',json = json_login)
    stok = eval(r0.text)['stok']
    
    content_htm = 'http://192.168.0.1/stok=%s/pc/Content.htm'%stok
    rrr = s.get(content_htm)
    
    post_url = 'http://192.168.0.1/stok=%s/ds'%stok
    json_disconnect = {"network":{"change_wan_status":{"proto":"pppoe","operate":"disconnect"}},
            "method":"do"}
    rrr = s.post(post_url,json = json_disconnect)
    time.sleep(60)
    ping_times = 0
    while os.system('ping baidu.com -n 1') !=0 :
        if ping_times<3:
            ping_times +=1
            print('网络未连接，重新尝试ping%d次/3次'%ping_times)
            time.sleep(10)
        else:
            print('网络重连失败')
            return 1
    print('网络重连成功',end = ',')
    json_ip = {"network":{"name":["wan_status"]},"method":"get"}
    ip = eval(s.post(post_url,json = json_ip).text)['network']['wan_status']['ipaddr']
    
    print('ip为%s'%ip)
    return 0
    
        
        
        
    
#
#json_connect = {"network":{"change_wan_status":{"proto":"pppoe","operate":"connect"}},
#        "method":"do"}
#s.post(post_url ,json = json_connect)








