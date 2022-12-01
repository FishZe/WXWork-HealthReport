from apscheduler.schedulers.background import BackgroundScheduler

from HealthReport import *
from Api import Api
from Notice import Notice


if __name__ == "__main__":
    with open("./json/cookies.json", "r") as f:
        cookies = json.load(f)

    if cookies == [] or cookies is None or cookies == {}:
        n = Notice()
        n.notice("error", "Cookies Error", "Please set your cookies in json/cookies.json")
        exit(0)

    cookies['wedrive_uin'] = cookies['wwapp.vid']
    api = Api(cookies)
    if not startChecker(api):
        n = Notice()
        n.notice("error", "Start Checker Error", "Start checker error, please check your cookies.")
        exit(0)
    else:
        n = Notice()
        n.notice("info", "Start Checker Success", "Start checker success!")
    reportId = getReportId(api)
    schedule = BackgroundScheduler()
    schedule.add_job(api.getUserInfo, 'interval', seconds=300, timezone='Asia/Shanghai')
    schedule.add_job(cornReport, 'cron', hour='0', minute='0', second='30', timezone='Asia/Shanghai', args=[api, reportId])
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
