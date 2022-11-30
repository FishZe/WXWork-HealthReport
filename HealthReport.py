import json
import time

from Api import Api
from Notice import Notice


# 获取单个问题答案
def getQuestionAnswer(item: dict) -> dict:
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
        answer = ""
        if "reply_type" in item.keys() and item['reply_type'] == 5:
            # 获取定位题目
            print(
                "This question need your location, you can choose to: \n\t1. input your location(json string) \n\t2. use auto location(NJUPT):")
            print("Please input your answer(number), end with enter: ", end=" ")
            choice = int(input())
            if choice == 1:
                print("Please input your location(json string): ", end=" ")
                answer = input()
            elif choice == 2:
                answer = '{"type":"","nation":"中国","province":"江苏省","city":"南京市","district":"栖霞区","addr":"江苏省南京市南京邮电大学(仙林校区)","lat":32.11586,"lng":118.9333,"module":"wework-native","exportText":"江苏省南京市南京邮电大学(仙林校区)"}'
        else:
            print("This question has no option, please input your text answer, end with enter: ", end=" ")
            answer = input()
        res['text_reply'] = answer
    return res


# 获取所有答案 带有问题更新检测
def getAllAnswer(items: list) -> list:
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
            answer.append(getQuestionAnswer(i))
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
        for i in items:
            if "status" in i.keys() and i["status"] == 2:
                # 该题目被禁用
                continue
            if i in originReport:
                # 问题已经存在
                for j in originAnswer:
                    # 找到原有的的答案
                    if j['question_id'] == i['question_id']:
                        answer.append(j)
                        break
            else:
                # 问题不存在
                answer.append(getQuestionAnswer(i))
        # 更新答案和问题
        with open("./json/answer.json", "w") as f:
            f.write(json.dumps(answer))
        with open("./json/report.json", "w") as f:
            f.write(json.dumps(items))
    else:
        # 问题未更新
        answer = originAnswer
    return answer


# 提交报告
def cornReport(api, formId, answerId=-1):
    n = Notice()
    n.notice("info", "Report", "Start to report!")
    questions = api.getReportInfo(formId)
    if questions == [] or questions is None or questions == {}:
        n.notice("error", "Report Error", "Get report info error, please check your cookies and try again later.")
        time.sleep(10)
        cornReport(api, formId, answerId)
        return
    answers = getAllAnswer(questions['form']['question']['items'])
    api.submitReport(answers, formId, answerId)
    time.sleep(1)
    reportInfo = api.getReportInfo(formId)
    if "answer_id" not in reportInfo.keys():
        n = Notice()
        n.notice("error", "Report error", "Report Failed! I will try again in 10 seconds.")
        time.sleep(10)
        cornReport(api, formId)
    else:
        n = Notice()
        n.notice("success", "Auto Health Report Success",
                 "Submit Success! Your answer id is " + str(reportInfo['answer_id']))


# 获取报告的id
def getReportId(api) -> str:
    reportList = api.getReportList()
    with open("./json/data.json", "r") as f:
        userData = json.load(f)
    if "formId" in userData.keys():
        # 已经获取过
        for i in reportList['form_items']:
            if i['form_id'] == userData['formId'] or \
                    i['form_id'] == f"{userData['formId']}{(int(time.time()) - int(time.time() - time.timezone) % 86400)}":
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
        print(f"\t{i}. {reportList['form_items'][i]['title']}: {reportList['form_items'][i]['note']}. Creator: {reportList['form_items'][i]['template_creater_name']}")
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


def startChecker(api: Api) -> bool:
    userInfo = api.getUserInfo()
    if userInfo == {}:
        return False
    n = Notice()
    n.notice("info", "Hello", f"{userInfo['user_list'][0]['name']} in {userInfo['root_party']['party_name']}")
    reportId = getReportId(api)
    reportInfo = api.getReportInfo(reportId)
    if reportInfo == [] or reportInfo is None or reportInfo == {}:
        n.notice("error", "Get Report Error", "Get report question error, please check your report.")
        return False
    getAllAnswer(reportInfo['form']['question']['items'])
    if "answer_id" in reportInfo.keys():
        n.notice("info", "Report", f"You have already submitted the report, your id is {reportInfo['answer_id']}")
    else:
        n.notice("info", "Report", f"You haven't submitted the report, I'll submit it for you.")
        cornReport(api, reportId)
    return True
