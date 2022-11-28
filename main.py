import time

import json
from apscheduler.schedulers.background import BackgroundScheduler

from Api import Api
from Notice import Notice


# 获取问题答案
def getQuestionAnswer(item):
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
            # 获取定位题目
            print("This question need your location, you can choose to: \n\t1. input your location(json string) \n\t2. use auto location(NJUPT):")
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


def getAllAnswer(items):
    with open("./json/answer.json", "r") as f:
        originAnswer = json.load(f)
    if originAnswer == [] or originAnswer is None or originAnswer == {}:
        # 未设置答案 或 答案为空
        answer = []
        for i in items:
            if "status" in i.keys() and i["status"] == 2:
                # 该题目被禁用
                continue
            answer.append(getQuestionAnswer(i))
        originAnswer = answer
        with open("./json/answer.json", "w") as f:
            f.write(json.dumps(answer))
        with open("./json/report.json", "w") as f:
            f.write(json.dumps(items))
    return originAnswer


def cornReport(api):
    n = Notice()
    n.notice("info", "Report", "Start to report!")
    reportInfo = api.getReportInfo()
    questions = reportInfo['question']['items']
    answers = getAllAnswer(questions)
    with open("./json/report.json", "r") as f:
        originQuestions = json.load(f)
    if questions != originQuestions:
        # 题目有变化
        n = Notice()
        n.notice("warning", "Report Content Changed", "Please Update Your Answer")
        newAnswers = []
        for i in questions:
            if i not in originQuestions and not ("status" in i.keys() and i["status"] == 2):
                # 有新题目 且 该题目未被禁用
                nowAnswer = getQuestionAnswer(i)
                for j in answers:
                    if j['question_id'] == nowAnswer['question_id']:
                        newAnswers.append(nowAnswer)
                        break
                    else:
                        newAnswers.append(j)
                answers = newAnswers
        with open("./json/answer.json", "w") as f:
            f.write(json.dumps(answers))
        with open("./json/report.json", "w") as f:
            f.write(json.dumps(questions))
    api.submitReport(answers)


if __name__ == "__main__":
    with open("./json/cookies.json", "r") as f:
        cookies = json.load(f)

    api = Api(cookies)
    api.getUserInfo()
    cornReport(api)
    schedule = BackgroundScheduler()
    schedule.add_job(api.getUserInfo, 'interval', seconds=300)
    schedule.add_job(cornReport, 'cron', hour='0', minute='0', second='0', args=[api])
    schedule.start()

    while True:
        time.sleep(10)

