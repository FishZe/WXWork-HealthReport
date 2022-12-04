import json
import time
from apscheduler.schedulers.background import BackgroundScheduler

from Api import Api
from Notice import Notice


def getSearchLocation(api) -> dict:
    print("Please input your city: ", end=" ")
    city = input()
    print("Please input your location keyword (like \"南京站\"): ", end=" ")
    keyword = input()
    page = 1
    res = []
    print("Searching for your location, please wait...")
    while True:
        data, c = api.searchLocation(keyword, city, page)
        res += data
        if page * 20 >= c:
            break
        page += 1
        time.sleep(0.5)
    print("Please choose your location: ")
    page = int(len(res) / 10)
    if len(res) % 10 != 0:
        page += 1
    i = 0
    while i < page:
        print(f"Page {i + 1}:")
        for j in range(10):
            if i * 10 + j >= len(res):
                break
            print(
                f"\t{i * 10 + j + 1}. {res[i * 10 + j]['title']} ({res[i * 10 + j]['category']}): {res[i * 10 + j]['address']}")
        print(
            "If you need to change page, please input \"n\" to next page, input \"p\" to previous page, input \"q\" to quit.")
        print("Please input your answer(number), end with enter: ", end=" ")
        answer = input()
        if answer == "n":
            i += 1
        elif answer == "p":
            if i == 0:
                print("This is the first page.")
                continue
            else:
                i -= 1
        elif answer == "q":
            return {}
        else:
            answer = int(answer)
            answer -= 1
            while answer not in range(0, len(res)):
                print("Your answer is not in the sections, please input your answer agine: ", end=" ")
                answer = int(input())
            return {
                "type": "",
                "nation": "中国",
                "province": res[answer]['province'],
                "city": res[answer]['city'],
                "district": res[answer]['district'],
                "addr": res[answer]['title'],
                "lat": res[answer]['location']['lat'],
                "lng": res[answer]['location']['lng'],
                "module": "wework-native",
                "exportText": res[answer]['title']
            }


def getLocationAnswer(api) -> str:
    """
        获取定位答案
        :param api: 已填入cookies的api
        :return str: 答案
    """
    answer = ""
    print("This question need your location, you can choose to:")
    print("\t1. input your location (json string):")
    print("\t2. use NJUPT's location (if you are in NJUPT):")
    print("\t3. use your IP to get location (not recommend):")
    print("\t4. search for your location in tencent map:")
    print("Please input your answer(number), end with enter: ", end=" ")
    choice = int(input())
    while choice not in [1, 2, 3, 4]:
        print("Your answer is not in the sections, please input your answer agine: ", end=" ")
        choice = int(input())
    if choice == 1:
        print("Please input your location(json string): ", end=" ")
        answer = input()
    elif choice == 2:
        answer = json.dumps({
            "type": "",
            "nation": "中国",
            "province": "江苏省",
            "city": "南京市",
            "district": "栖霞区",
            "addr": "南京邮电大学(仙林校区)",
            "lat": 32.113554,
            "lng": 118.93085,
            "module": "wework-native",
            "exportText": "南京邮电大学(仙林校区)"
        })
        print(
            f"NJUPT's location: {json.loads(answer)['province']} {json.loads(answer)['city']} {json.loads(answer)['district']} {json.loads(answer)['addr']}")
    elif choice in [3, 4]:
        if choice == 3:
            answer = api.getGeolocation()
        else:
            answer = getSearchLocation(api)
            if answer == {}:
                getSearchLocation(api)
        print(
            f"Your location: {answer['province']} {answer['city']} {answer['addr']}, do you want to use it? (y/n): ",
            end="")
        choice = input()
        while choice not in ["y", "n"]:
            print("Your answer is not in the sections, please input your answer agine: ", end=" ")
            choice = input()
        if choice == "n":
            print("Please re-input your choice.")
            return getLocationAnswer(api)
        answer = json.dumps(answer)
    return answer


def getQuestionAnswer(item: dict, api) -> dict:
    """
        获取单个问题答案
        :param item: 问题
        :param api: 已经填入cookies的api
        :return dict: 答案
    """
    print(f"Question {item['question_id']}: {item['title']}")
    res = {"question_id": item['question_id'], "text_reply": "", "option_reply": []}
    if len(item['option_item']) != 0:
        # 选择题
        section = []
        for i in item['option_item']:
            if "status" in i.keys() and i["status"] == 2:
                # 该选项被禁用
                continue
            section.append(i['key'])
            print(f"    Option {i['key']}: {i['value']}")
        print("Please input your answer(number), end with enter: ", end=" ")
        answer = int(input())
        while answer not in section:
            # 选择题答案不在选项中
            print("Your answer is not in the sections, please input your answer agine: ", end=" ")
            answer = int(input())
        res['option_reply'] = [answer]
    else:
        # 填空题
        if "reply_type" in item.keys() and item['reply_type'] == 5:
            answer = getLocationAnswer(api)
        else:
            # 获取普通填空题目
            print("This question has no option, please input your text answer, end with enter: ", end=" ")
            answer = input()
        res['text_reply'] = answer
    return res


def getAllAnswer(items: list, api) -> list:
    """
        获取所有答案
        :param items: 问题列表
        :param api: 已经填入cookies的api
        :return list: 答案列表
    """
    with open("./json/answer.json", "r") as f:
        originAnswer = json.load(f)
    with open("./json/report.json", "r") as f:
        originReport = json.load(f)
    if originAnswer == [] or originAnswer is None or originAnswer == {}:
        # 未设置答案
        n = Notice()
        n.notice("warning", "Answer not set", "You have not set your answer, please set your answer in the console.")
        answer = []
        for i in items:
            if "status" in i.keys() and i["status"] == 2:
                # 该题目被禁用
                continue
            answer.append(getQuestionAnswer(i, api))
        # 更新答案和问题
        with open("./json/answer.json", "w") as f:
            f.write(json.dumps(answer))
        with open("./json/report.json", "w") as f:
            f.write(json.dumps(items))
    # TODO: 以下内容的时间复杂度较高，未来可以考虑优化
    elif originReport != items:
        # 问题更新
        n = Notice()
        n.notice("warning", "Question updated",
                 "The question has been updated, please update your answer in the console.")
        answer = []
        rawReport = rawAnswer = {}
        for i in originAnswer:
            rawAnswer[i['question_id']] = i
        for i in items:
            rawReport[i['question_id']] = i
        for i in items:
            if "status" in i.keys() and i["status"] == 2:
                # 该题目被禁用
                continue
            if i in originReport:
                # 问题已经存在（未发生修改）
                answer.append(rawAnswer[i['question_id']])
            else:
                # 问题不存在
                answer.append(getQuestionAnswer(i, api))
        # 更新答案和问题
        with open("./json/answer.json", "w") as f:
            f.write(json.dumps(answer))
        with open("./json/report.json", "w") as f:
            f.write(json.dumps(items))
    else:
        # 问题未更新
        answer = originAnswer
    return answer


def getReportAnswer(api, formId):
    questions = api.getReportInfo(formId)
    if questions == [] or questions is None or questions == {}:
        n = Notice()
        n.notice("error", "Report Error", "Get report info error, please check your cookies and try again later.")
        time.sleep(10)
        return getReportAnswer(api, formId)
    answers = getAllAnswer(questions['form']['question']['items'], api)
    return answers


def refillAnswer(api, formId):
    """
        重新填写答案
        :param formId: 报告id
        :param api: 已经填入cookies的api
    """
    with open("./json/answer.json", "w") as f:
        f.write(json.dumps([]))
    getReportAnswer(api, formId)


def cornReport(api, formId, answerId=-1) -> bool:
    """
        提交报告
        :param api: 已经填入cookies的api
        :param formId: 报告id
        :param answerId: 已经提交过的报告Id, 默认为1时为初次提交, 否则为覆盖提交
        :return bool: 是否提交成功
    """
    n = Notice()
    n.notice("info", "Report", "Start to report!")
    answers = getReportAnswer(api, formId)   # 获取答案
    api.submitReport(answers, formId, answerId)
    time.sleep(1)
    reportInfo = api.getReportInfo(formId)
    if "answer_id" not in reportInfo.keys():
        n = Notice()
        n.notice("error", "Report error", "Report Failed! I will try again in 10 seconds.")
        time.sleep(10)
        return cornReport(api, formId)
    else:
        n = Notice()
        n.notice("success", "Auto Health Report Success",
                 "Submit Success! Your answer id is " + str(reportInfo['answer_id']))
        return True


# 获取报告的id
def getReportId(api) -> str:
    reportList = api.getReportList()
    with open("./json/data.json", "r") as f:
        userData = json.load(f)
    if "formId" in userData.keys():
        # 已经获取过
        for i in reportList['form_items']:
            if i['form_id'] == userData['formId'] or \
                    i[
                        'form_id'] == f"{userData['formId']}{(int(time.time()) - int(time.time() - time.timezone) % 86400)}":
                # 该报告仍然存在
                return userData['formId']
    if reportList == {} or reportList['form_items'] == []:
        n = Notice()
        n.notice("error", "Get Report List Error",
                 "Get report list error, please check if you have the report need to submit.")
        return ""
    reports = {}
    n = Notice()
    n.notice("warning", "Get Report List Warning",
             "You haven't set the report, please select the report you want to submit.")
    print("Please choose the report you want to submit:")
    for i in range(0, len(reportList['form_items'])):
        if reportList['form_items'][i]['form_id'][-10:] == str(
                int(time.time()) - int(time.time() - time.timezone) % 86400):
            reportId = reportList['form_items'][i]['form_id'][:-10]
        else:
            reportId = reportList['form_items'][i]['form_id']
        reports[i] = reportId
        print(
            f"\t{i}. {reportList['form_items'][i]['title']}: {reportList['form_items'][i]['note']}. Creator: {reportList['form_items'][i]['template_creater_name']}")
    print("Please input your choice(number), end with enter: ", end=" ")
    choice = int(input())
    while choice not in reports.keys():
        print("Your input is not in the report list, please input again, end with enter: ", end=" ")
        choice = int(input())
    reportId = reports[choice]
    userData['formId'] = reportId
    with open("./json/data.json", "w") as f:
        f.write(json.dumps(userData))
    return reportId


def getApi() -> Api:
    with open("./json/cookies.json", "r") as f:
        cookies = json.load(f)
    if cookies == [] or cookies is None or cookies == {}:
        n = Notice()
        n.notice("error", "Cookies Error", "Please set your cookies in json/cookies.json")
        exit(0)
    cookies['wedrive_uin'] = cookies['wwapp.vid']
    api = Api(cookies)
    return api


def startChecker(api: Api) -> tuple:
    userInfo = api.getUserInfo()
    if userInfo == {}:
        return False, None
    n = Notice()
    n.notice("info", "Hello", f"{userInfo['user_list'][0]['name']} in {userInfo['root_party']['party_name']}")
    reportId = getReportId(api)
    reportInfo = api.getReportInfo(reportId)
    if reportInfo == [] or reportInfo is None or reportInfo == {}:
        n.notice("error", "Get Report Error", "Get report question error, please check your report.")
        return False, None
    getAllAnswer(reportInfo['form']['question']['items'], api)
    if "answer_id" in reportInfo.keys():
        n.notice("info", "Report", f"You have already submitted the report, your id is {reportInfo['answer_id']}")
    else:
        n.notice("info", "Report", f"You haven't submitted the report, You can use \"re-submit\" arg to submit it.")
    return True, reportInfo['answer_id']


def check(api: Api) -> tuple:
    res, answerId = startChecker(api)
    if not res:
        n = Notice()
        n.notice("error", "Start Checker Error", "Start checker error, please check your cookies.")
        exit(0)
    else:
        n = Notice()
        n.notice("info", "Start Checker Success", "Start checker success!")
        return res, answerId


def startCorn(api: Api, reportId: str):
    schedule = BackgroundScheduler()
    schedule.add_job(api.getUserInfo, 'interval', seconds=300, timezone='Asia/Shanghai')
    schedule.add_job(cornReport, 'cron', hour='0', minute='0', second='30', timezone='Asia/Shanghai',
                     args=[api, reportId])
    schedule.start()
    while True:
        try:
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            schedule.shutdown()
            n = Notice()
            n.notice("info", "Exit", "Exit success!")
            break
        except Exception as e:
            n = Notice()
            n.notice("error", "Error", str(e))
            break
