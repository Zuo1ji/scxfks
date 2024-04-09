import time
import requests
from io import BytesIO
from PIL import Image
from lxml import etree
import threading
import hashlib
from predict import Predict,vkmodel

class mySession(requests.Session):
    def __init__(self) -> None:
        super().__init__()

    def login(self,username,md5Password,predict:Predict):
        res=self.get('http://xxpt.scxfks.com/study/captcha')
        image=Image.open(BytesIO(res.content))
        captcha=predict.predict(image)
        data={
            "mobile":username,
            "password":md5Password,
            "captcha":captcha
        }
        loginres=self.post('http://xxpt.scxfks.com/study/session',json=data)
        return loginres.status_code == 200
        
    def getClassLists(self,url='http://xxpt.scxfks.com/study/courses/all'):
        res=self.get(url)
        res.encoding='utf-8'
        tree = etree.HTML(res.text)
        classLists=['http://xxpt.scxfks.com'+i for i in tree.xpath('//tbody//tr/td[4]/a/@href')]
        return classLists
    
    def getCourseLists(self,urls:list,):
        courseLists=[]
        for url in urls:
            res=self.get(url=url)
            res.encoding='utf-8'
            tree = etree.HTML(res.text)
            courseLists+=tree.xpath("//td[@class='title']//div[2][not(contains(text(),'获得0.5学分'))]/../div[1]//@href")
        return courseLists
    
    def getUserScore(self):
        res=self.get('http://xxpt.scxfks.com/study/index')
        res.encoding='utf-8'
        tree = etree.HTML(res.content)
        try:
            username=tree.xpath("/html/body/section/div[1]/div/div[1]/div[1]/h3/text()")[0]#有百分之一的几率找不到
            score=tree.xpath("/html/body/section/div[1]/div/div[1]/div[3]/div[1]/text()")[0].split('：')[-1]
        except:
            username="天选之子"
            score="0"
        return username,score
    def getcookie(self):
        cookies=self.cookies
        cookie="; ".join([f"{c.name}={c.value}" for c in cookies])
        return cookie

    def saveRecord(self,cid,refer,classes="a_a_d"):
        self.get("http://xxpt.scxfks.com"+refer) #每次学习post的cookie会变，因此要先get一下更新cookie
        url="http://xxpt.scxfks.com/study/learnlog/"+cid+"/"+classes
        headers={
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Content-Length": "0",
            "Cookie": self.getcookie(),
            "Host": "xxpt.scxfks.com",
            "Origin": "http://xxpt.scxfks.com",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://xxpt.scxfks.com"+refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
        }
        res=self.post(url,headers=headers)
        return res.text == 'true'

def studyFlow(mobile,password,predict:Predict):
    mysession=mySession()
    mysession.get('http://xxpt.scxfks.com/study/login')
    md5=hashlib.md5((password+'gw-gd-exam').encode(encoding='utf-8')).hexdigest().upper()
    # #尝试登录3次（但由于这个验证码太简单以至于仅有千分之一的几率识别不到验证码）
    # isLogin=False
    # 
    # for i in range(3):
    #     isLogin=mysession.login(mobile,md5,predict)
    #     if isLogin:
    #         break
    #     print(f"{mobile}第{i+1}次登录失败，尝试重新登录！！ \n-----------------------")
    # if not isLogin:
    #     print(mobile+"登录失败！！！！！！！")
    #     return
    # print(mobile+"登录成功！！ \n-----------------------")
    # time.sleep(3)
    mysession.login(mobile,md5,predict)
    print(mobile+"登录成功！！ \n-----------------------")
    time.sleep(3)
    #打印当前学员成绩
    username,score=mysession.getUserScore()
    if int(score)>=100:
        print('\r'+username+"已学够100分，准备退出.....")
        return
    print('\r'+username+" 当前分数："+score+"  开始学习.....")
    #获取刑事类法律专题和民商事类专题
    #这两个专题课多足够学满100分,且分类都是a_a_d（后续的学习post后缀需要根据分类来）
    courseLists=mysession.getCourseLists(['http://xxpt.scxfks.com/study/course/3613',
                                         'http://xxpt.scxfks.com/study/course/3597'])

    #学5分
    if len(courseLists)<=10:
        return
    time.sleep(2)
    for i in range(10):
        courseid=courseLists[i].split('/')[-1]
        ok=mysession.saveRecord(courseid,courseLists[i])
        if ok:
            print(f"{username}第{i+1}篇学习完成！！！！！")
        else:
            print(f"{username}第{i+1}篇学习未完成，可能是由于今日5分已学完。。。。准备退出。。。。")
            return
        time.sleep(1)
    print('\r'+username+" 学习完成.....")

if __name__=='__main__':
    predict=Predict(r"path\to\your\model\path")
    users=[
        ['mobile0','password0'],
        ['mobile1','password1'],
    ]
    for user in users:
        _xuefa=threading.Thread(target=studyFlow,args=(user[0],user[1],predict))
        time.sleep(0.1)
        _xuefa.start()
