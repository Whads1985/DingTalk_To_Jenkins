# -*- coding: utf-8 -*-
import sys
import requests
import json
import time
import MySQLdb
from dingtalkchatbot.chatbot import DingtalkChatbot


# 初始化当前时间
nowtime = time.strftime("%Y-%m-%d", time.localtime())

###########################################################################################
## 配置项 ##
###########

# Mysql数据库连接
Mysql_Host = "192.168.1.1"
Mysql_User = "DTJ"
Mysql_Pass = "DTJ"
Mysql_Db   = "DingtalkToJenkins"
Mysql_Char = "utf8"

# 钉钉自定义机器人接口地址
dingtalk_call_url = "https://oapi.dingtalk.com/robot/send?access_token=你的token}"

# 浏览器 Header
headers = { 'Host': "aflow.dingtalk.com",
'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
'Cookie': "浏览器的COOKIE",
}

###########################################################################################
# Process Code 获取地址
searchurl="https://aflow.dingtalk.com/dingtalk/web/query/process/getAllProcess.json"

# Process Instance ID 获取地址
listurl = "https://aflow.dingtalk.com/dingtalk/web/query/instdata/getInstancesByQuery.json"

# 详细信息获取地址
detailurl="https://aflow.dingtalk.com/dingtalk/pc/query/form/getInstDetailData.json"


# 获取Process Code
searchbody="isNeedFormContent=false"
responseSearch = requests.request("POST", searchurl, data=searchbody, headers=headers)
responseSearchJson = json.loads(responseSearch.text)
try:
    processCode = responseSearchJson['data'][14]['processCode']
except:
    print ("Error: Can Not Found Process Code, MayBe Cookie Expired!!")
    exit()


# 获取 Process Instance ID
listbody = "page=1&appkey=ding30ed19fb5415d1d6&limit=10&createFrom=2018-07-05&createTo="+str(nowtime)+"&finishFrom=&finishTo=&processCode="+processCode+"&instanceStatus=COMPLETED&title=&businessId="
responseList = requests.request("POST", listurl, data=listbody, headers=headers)
responseJson = json.loads(responseList.text)
try:
    processInstanceIds = responseJson['data']['values']
except:
    print ("Error: Can Not Found Process Instance IDs ")
for item in processInstanceIds:
    processInstanceId = item['processInstanceId']

    # 打开连接并使用cursor()方法获取操作游标 
    db = MySQLdb.connect(Mysql_Host, Mysql_User, Mysql_Pass, Mysql_Db, charset=Mysql_Char) 
    cursor = db.cursor()
    
    sql = "select COUNT(1) from run_log where ProcessInstanceID = '%s'" %(processInstanceId)
    try:
        cursor.execute(sql)
        results = cursor.fetchone()[0]
        if (str(results) != "0"):
            print("Process Instance ID: %s Is Exist.") %(processInstanceId)
            continue
    except:
        print (cursor.execute(sql))
    db.close()

    # 根据获取到的Process Instance ID 请求详细内容
    detailbody = "__Pages.getApprovalInfo()__=&procInstId=%s&__asp=dingtalk" %(processInstanceId)
    responseDetail = requests.request("POST", detailurl, data=detailbody, headers=headers)
    try:
        responseDetailJson = json.loads(responseDetail.text)
        # 获取项目名
        processName = responseDetailJson['data']['formData']['DDSelectField-JFQIPCDQ']['value']
        # 获取提交的用户
        processUser = responseDetailJson['data']['originatorInfo']['name']
        # 获取订单号
        businessId = responseDetailJson['data']['formData']['pmc_business_id']['value']
        # 获取订单状态
        resultType = responseDetailJson['data']['result']
    except:
        print (responseDetailJson)

    # 获取提交用户的手机号
    db = MySQLdb.connect(Mysql_Host, Mysql_User, Mysql_Pass, Mysql_Db, charset=Mysql_Char)
    cursor = db.cursor()
    sql = "select phone from user where name = '%s'" %(processUser)
    try:
        cursor.execute(sql)
        results = cursor.fetchone()
    except:
        print ("Error: Can Not Connect To Database!")
    try:        
        processUserPhone = results[0]
    except:
        processUserPhone = "13900000000"
    db.close()

    
    
    JenkinsStatus = ""
    if (str(resultType) == 'agree'):
        # 通过 processName 获取配置
        db = MySQLdb.connect(Mysql_Host, Mysql_User, Mysql_Pass, Mysql_Db, charset=Mysql_Char)
        cursor = db.cursor()
        sql = "select * from config where processName = '%s'" %(processName)

        try:
            cursor.execute(sql)
            results = cursor.fetchone()
            JenkinsUrl = results[2]
            JenkinsToken = results[3]
            url = "%sbuild?token=%s" % (JenkinsUrl, JenkinsToken)           
        except: 
            print ("Error:Can Not Found %s, Please Check Database Config!!!" % (processName))
            continue
        db.close()

        # 发起Jenkins请求
        try:
            responseJenkins = requests.request("GET", url, headers=headers)                                      
        except:
            print ("Error: Can Not Connect %s Jenkins Server") % (processName)
            continue

        if (str(responseJenkins.status_code) != '201'):
            JenkinsStatus = "False"
        else:
            JenkinsStatus = "Success"
            # 成功后发送钉钉消息
            xiaoding = DingtalkChatbot(dingtalk_call_url)
            at_mobiles = ['%s' % (processUserPhone)]
            dingtalk_msg = u"[Jenkins]：@%s 您提交的%s上线申请已通过审批,现在Jenkins正在开始构建,详情请访问:%s" % (processUser, processName, JenkinsUrl)

            try:
                if ( str(processUserPhone) == '13900000000'):
                    xiaoding.send_text(msg=dingtalk_msg)
                else:
                    xiaoding.send_text(msg=dingtalk_msg, at_mobiles=at_mobiles)
                
            except:
                print ("Error: DingTalk Send Filed")
                print (dingtalk_msg)


        




    # 打开连接并使用cursor()方法获取操作游标 
    db = MySQLdb.connect(Mysql_Host, Mysql_User, Mysql_Pass, Mysql_Db, charset=Mysql_Char)
    cursor = db.cursor()

    sql = "insert into run_log (ProcessInstanceID,businessID,Name,User,DingTalkResult,JenkinsResult) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (processInstanceId, businessId, processName,processUser,resultType,JenkinsStatus)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        print ("Process Instance ID: "+processInstanceId+" Insert To DataBase") 
        db.commit()
        
    except:
        db.rollback  
    db.close()
