"""
Created on Fri Jun 14 13:50:49 2019

@author: chingyichen
"""

from googletrans import Translator
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
import requests
from bs4 import BeautifulSoup
from linebot.models import *
import re


def bot_get_wiki(keyword):
    response=requests.get("https://zh.wikipedia.org/zh-tw/"+keyword) 

    bs=BeautifulSoup(response.text,"lxml")
    p_list=bs.find_all("p")
    for p in p_list:
        if keyword in p.text[0:10]:
            return p.text

app = Flask(__name__)

# 必須放上Channel Access Token
line_bot_api = LineBotApi('Channel Access Token')
# 必須放上Channel Secret
handler = WebhookHandler('Channel Secret')
# 必須放上Your user ID
line_bot_api.push_message('user ID', TextSendMessage(text='你可以開始了'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
control=""
lang=""

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 取得個人資料
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name
    uid = profile.user_id

    print('uid: '+uid)
    print('name:'+nameid)
    global control
    global lang
    lang_dic = {"1":"zh-tw","2":"en","3":"ja","4":"ko","5":"th","6":"vi","7":"id","8":"fr","9":"ru","10":"de",}


    # 傳送圖片
    if event.message.text == '我要結束！！':
         message = TextSendMessage(text="已結束")        
         line_bot_api.reply_message(event.reply_token,message)  
         control=""
         
    elif control=="我要翻譯的語句或詞語":
        translate=Translator()
        
        result = translate.translate(event.message.text,dest=lang)      
        message = TextSendMessage(text=result.text)
        line_bot_api.reply_message(event.reply_token,message)   
         
    elif control == '我要翻譯的語言':
        message = TextSendMessage(text="請輸入欲翻譯的語句或單詞，若欲結束翻譯請輸入“我要結束！！”")
        line_bot_api.reply_message(event.reply_token,message)
        lang=lang_dic[event.message.text]
        control="我要翻譯的語句或詞語"
        
    elif event.message.text == '翻譯':
        message = TextSendMessage(text="請輸入欲翻譯的語言\n1:中文\n2:英文\n3:日文\n4:韓文\n5:泰文\n6:越南文\n7:印尼文\n8:法文\n9:俄文\n10:德文\n，若欲結束翻譯請輸入“我要結束！！”")
        line_bot_api.reply_message(event.reply_token,message)
        control="我要翻譯的語言"
        
    elif control=='我要查詢的的字詞':
        content=bot_get_wiki(event.message.text)
        if content!=None:
            content=re.sub(r'\[[^\]]*\]','',content)
            
            message = TextSendMessage(text=content)
            line_bot_api.reply_message(event.reply_token,message)
            
        else:
            message = TextSendMessage(text="找不到相關資料")
            line_bot_api.reply_message(event.reply_token,message)
        
        
        
    elif event.message.text =="查詢":
        message = TextSendMessage(text="請輸入欲查詢的語句或單詞，若欲結束查詢請輸入“我要結束！！")
        line_bot_api.reply_message(event.reply_token,message)
        control="我要查詢的的字詞"


    else:
        message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token,message)



if __name__ == '__main__':
    app.run(debug=True)
