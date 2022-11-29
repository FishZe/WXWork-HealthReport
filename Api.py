import json
import time
import requests

from Notice import Notice


class Api():
    def __init__(self, cookies):
        self.cookies = cookies
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36 Language/zh wxwork/4.0.19 (MicroMessenger/6.2) WindowsWechat  MailPlugin_Electron WeMail embeddisk",
            "origin": "https://work.weixin.qq.com",
        }

    def getUserInfo(self) -> bool:
        n = Notice()
        n.notice("info", "Auto Health Report Info", "Try to get user info")
        url = f"https://work.weixin.qq.com/healthreport/getuserpartyinfo"
        r = requests.post(url,
                          headers=self.headers,
                          cookies=self.cookies,
                          data={"operatorid": self.cookies['wedrive_uin'], "vids": self.cookies['wedrive_uin']})
        res = json.loads(r.text)
        if res['result']['errCode'] != 0:
            n = Notice()
            n.notice("error", "Auto Health Report Error", "Your cookies may be expired, please update your cookies.json file.")
            return False
        return True

    def getReportInfo(self):
        url = f"https://work.weixin.qq.com/healthreport/share?_t={time.time()}&f=json&form_id=AGkA4wfzAA0_AGkA4wfz-A0AH8AtgaFAFoxwj9N5t3Ql{int(time.time()) -int(time.time()-time.timezone) % 86400}"
        r = requests.post(url, headers=self.headers, cookies=self.cookies)
        res = json.loads(r.text)
        return res['data']

    def submitReport(self, answer):
        url = "https://work.weixin.qq.com/healthreport/share?f=json"
        data = {
            "key":  (None, ""),
            "form_id": (None, f"AGkA4wfzAA0_AGkA4wfz-A0AH8AtgaFAFoxwj9N5t3Ql{int(time.time()) -int(time.time()-time.timezone) % 86400}"),
            "type": (None, "2"),
            "form_reply": (None, json.dumps({"items": answer})),
            "f": (None, "json"),
            "source": (None, "hb_noticard"),
            "vscode": (None, "null"),
        }
        try:
            r = requests.post(url, headers=self.headers, cookies=self.cookies, files=data)
            res = json.loads(r.text)
            if res['result']['errCode'] != 0:
                n = Notice()
                n.notice("error", "Auto Health Report Error", "Submit Error, please check your cookies and update cookies.json")
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Auto Health Report Error", "Unknown Error, please copy the error information and make a new issue to me")
