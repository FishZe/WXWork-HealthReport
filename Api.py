import json
import time
import requests

from Notice import Notice


class Api:
    def __init__(self, cookies):
        self.cookies = cookies
        self.expire = False
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36 Language/zh wxwork/4.0.19 (MicroMessenger/6.2) WindowsWechat  MailPlugin_Electron WeMail embeddisk",
            "origin": "https://work.weixin.qq.com",
        }

    def getUserInfo(self) -> dict:
        if self.expire:
            return {}
        n = Notice()
        n.notice("info", "Auto Health Report Info", "Try to get user info")
        url = f"https://work.weixin.qq.com/healthreport/getuserpartyinfo"
        try:
            r = requests.post(url,
                              headers=self.headers,
                              cookies=self.cookies,
                              data={"operatorid": self.cookies['wedrive_uin'], "vids": self.cookies['wedrive_uin'],
                                    "need_root_party": "true"})
            res = json.loads(r.text)
            if res['result']['errCode'] != 0:
                self.expire = True
                n = Notice()
                n.notice("error", "Auto Health Report Error",
                         "Your cookies may be expired, please update your cookies.json file.")
                return {}
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Auto Health Report Error",
                     "Unknown Error occurred when getting user info, please copy the error information and make a new issue to me")
            return {}
        return res['data']

    def getReportList(self) -> dict:
        url = "https://work.weixin.qq.com/healthreport/healthformlist"
        try:
            r = requests.post(url, headers=self.headers, cookies=self.cookies, data={"source": "0"})
            res = json.loads(r.text)
            if res['result']['errCode'] != 0:
                n = Notice()
                n.notice("error", "Get Report Lists Error", "I'll tried it later.")
                time.sleep(5)
                return self.getReportList()
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Get Report Lists Error",
                     "Unknown Error occurred when getting report lists, please copy the error information and make a new issue to me")
            return {}
        return res['data']

    def getReportInfo(self, formId) -> dict:
        url = f"https://work.weixin.qq.com/healthreport/share?_t={time.time()}&f=json&form_id={formId}{int(time.time()) - int(time.time() - time.timezone) % 86400}"
        try:
            r = requests.post(url, headers=self.headers, cookies=self.cookies)
            res = json.loads(r.text)
            if res['result']['errCode'] != 0:
                n = Notice()
                n.notice("error", "Get Report Info Error", "I'll tried it later.")
                return self.getReportInfo(formId)
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Get Report Info Error",
                     "Unknown Error occurred when getting report info, please copy the error information and make a new issue to me")
            return {}
        return res['data']

    def submitReport(self, answer, formId, answerId=-1):
        url = "https://work.weixin.qq.com/healthreport/share?f=json"
        data = {
            "key": (None, ""),
            "form_id": (None, f"{formId}{int(time.time()) - int(time.time() - time.timezone) % 86400}"),
            "type": (None, "2"),
            "form_reply": (None, json.dumps({"items": answer})),
            "f": (None, "json"),
            "source": (None, "hb_noticard"),
            "vscode": (None, "null"),
        }
        if answerId != -1:
            data["modify_answer_id"] = (None, answerId)
            data['type'] = (None, "3")
        try:
            r = requests.post(url, headers=self.headers, cookies=self.cookies, files=data)
            res = json.loads(r.text)
            if res['result']['errCode'] != 0:
                n = Notice()
                n.notice("error", "Auto Health Report Error",
                         "Submit Error, please check your cookies and update cookies.json")
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Auto Health Report Error",
                     "Unknown Error occurred when submitting the report, please copy the error information and make a new issue to me")

    def getGeolocation(self) -> dict:
        url = "https://apis.map.qq.com/ws/location/v1/ip?key=TKUBZ-D24AF-GJ4JY-JDVM2-IBYKK-KEBCU"
        try:
            r = requests.get(url, headers=self.headers)
            res = json.loads(r.text)
            if res['status'] != 0:
                n = Notice()
                n.notice("error", "Get Geolocation Error", "I'll tried it again.")
                time.sleep(1)
                return self.getGeolocation()
        except Exception as e:
            print(e)
            n = Notice()
            n.notice("error", "Get Geolocation Error",
                     "Unknown Error occurred when getting geolocation, please copy the error information and make a new issue to me")
            return {}
        return {"module": "geolocation",
                "type": "ip",
                "accuracy": 10000,
                "adcode": res['result']['ad_info']['adcode'],
                "nation": res['result']['ad_info']['nation'],
                "province": res['result']['ad_info']['province'],
                "city": res['result']['ad_info']['city'],
                "lat": res['result']['location']['lat'],
                "lng": res['result']['location']['lng'],
                "addr": f"{res['result']['ad_info']['province']}{res['result']['ad_info']['city']}{res['result']['ad_info']['district']}({res['result']['location']['lng']},{res['result']['location']['lat']})",
                "exportText": f"{res['result']['ad_info']['province']}{res['result']['ad_info']['city']}{res['result']['ad_info']['district']}({res['result']['location']['lng']},{res['result']['location']['lat']})"
                }
