# -*- coding: UTF-8 -*-
import binascii
import os
import re
import shutil
import urllib
import urllib2

import httplib2
from pip._vendor.requests.api import request
from cgitb import html


rootdir = 'LofterPhotos/'  
if os.path.exists(rootdir):
    print u'文件夹' + rootdir + u'已存在，无需再次创建'
else:
    os.makedirs(rootdir)
    print u'文件夹' + rootdir + u'已创建'

# 读取lofter首页地址列表，存到lofterlist中
filelofterlist = os.path.curdir + '\lofterlist.txt'
fp = open(filelofterlist, 'r')  
lofterlist = fp.readlines() 
for i in range(len(lofterlist)):  
    lofterlist [i] = lofterlist [i][:-1]  
fp.close() 

filecookielist = os.path.curdir + '\cookielist.txt'
fp2 = open(filecookielist, 'r')  
cookielist = fp2.readlines() 
for i in range(len(cookielist)):  
    cookielist [i] = cookielist [i][:-1]  
fp2.close()

# http://wanimal.lofter.com/
# <html>--<body>--<div id="main">--<!-- 图片 --><div class="post photopost id-152964721">            
# 图片地址http://imglf2.nosdn.127.net/img/TEE5d013Zkl3SHpJbS83RHBES0N4ZE1EZnJtMFVsQzZ4TUh0UmM5MUp2SVJ1YVlHaTRGc2dBPT0.jpg?imageView&thumbnail=1680x0&quality=96&stripmeta=0&type=jpg
# 图片地址http://imglf6.ph.126.net/ZhPybsaVNtRQ4qV-Nx96JQ==/6597999953494367536.jpg
# 需要cookies或referer
# cookieStr = 'usertrack=c+xxC1ZJaMsA3KiIA605Ag==; _ntes_nnid=23c2474f57c3418520dd7e1450e83955,1448269702106; __utma=61349937.779240437.1448269703.1449040460.1449042287.7; __utmz=61349937.1449033996.5.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; JSESSIONID-WLF-XXD=5fcd05478500e825d122fd1a29aa33af5d5d11cd6dc46d28023d90a06634a6498234242d89562480d5462768849bf8ad77b9158e38ca91560f628dcda757159bff3d7ee67fa088927f226a02744df7bd0172c0d9c032bdbe5498bffacc797a4f1579a3e49e65ff064b6fb559070420a7c858b8c189172622bbaceb4c5a8b001722a5aa5c; reglogin_hasopened=1; firstentry=%2FblogPhotoAd.do%3FX-From-ISP%3D2%26positionId%3D3%26callback%3Dnb.m.g.cbGetBlogTopAd|http%3A%2F%2Fzxkh19501.blog.163.com%2Fblog%2Fstatic%2F123785179201211361432988%2F; reglogin_isLoginFlag=; reglogin_isLoginFlag=; __utmc=61349937; __utmb=61349937.10.8.1449042719382'


for cookie in cookielist:
    if len(cookie) == 0 :  # 防止因为出现空行删除所有照片  
        continue
    if cookie.startswith('#'):  # 忽略以#号开头的行
        continue
    cookieStr1 = cookie
headers = {'Cookie': cookieStr1}  
h = httplib2.Http() 


for target in lofterlist:
    if len(target) == 0 :  # 防止因为出现空行删除所有照片  
        continue
    if target.startswith('#'):  # 忽略以#号开头的行
        continue
    url = target 
    # url = 'http://wanimal.lofter.com/'
    # url = 'http://joejock.lofter.com/'
    # url = 'http://numberw.lofter.com/'
    targeturl = url
    print u'url地址' + targeturl
    if None == re.search(r'http:\/\/(?P<domain>\S*).lofter.com\/', url):
        continue
    userdomain = re.search(r'http:\/\/(?P<domain>\S*).lofter.com\/', url).group('domain')
    print u'当前用户' + userdomain
    dir = rootdir + userdomain + '/'
    try:
        os.makedirs(dir)  # 建立相应的文件夹
    except:
        shutil.rmtree(dir)  # 无论文件夹是否为空都移除该文件夹
        os.makedirs(dir)
    resp, content = h.request(url, 'GET', headers=headers)
    
    # 正则解析首页图片
    rex = r'img src=\"(?P<src>\S*)\"'
    photoList = re.findall(rex, content)
    # 正则解析剩余页的链接参数
    rex = r'\"page_number\" href=\"(?P<src>\S*)\"'
    pageList = re.findall(rex, content)
    # 解析剩余页面的图片链接
    for paras in pageList:
        url = targeturl + paras
        resp, content = h.request(url, 'GET', headers=headers)
        rex = r'img src=\"(?P<src>\S*)\"'
        tmplist = re.findall(rex, content)
        photoList.extend(tmplist)
    
    print u'解析完成,' + u'图片数量' + str(len(photoList))
    
    # 下面是下载图片和保存图片
    count = 0
    for photourl in photoList:
        url = photourl
        print url  
        resp = None
        content = None       
        resp, content = h.request(url) 
        fmt = binascii.b2a_hex(content[0:4])  # 读取前4字节转化为16进制字符串
        print fmt  
        phototype = {'47494638': '.gif', 'ffd8ffe0': '.jpg', 'ffd8ffe1': '.jpg', 'ffd8ffdb': '.jpg', '89504e47': '.png'}  # 智能识别文件格式             
        count = count + 1   
        filename = 'picture' + str(count)
        print filename
        qualified_file_name = dir + filename + phototype[fmt]  
        open(qualified_file_name, 'wb').write(content) 
    print userdomain + u'的图片下载完成'

print u'所有图片下载完成'
