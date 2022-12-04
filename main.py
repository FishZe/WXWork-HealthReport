import sys

from HealthReport import *


if __name__ == "__main__":
    api = getApi()
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        arg = ""
    if arg == "refill":
        refillAnswer(api, getReportId(api))
    elif arg == "re-submit":
        res, answerId = check(api)
        cornReport(api, getReportId(api), answerId)
    elif arg in ["", None, "start"]:
        res, answerId = check(api)
        startCorn(api, getReportId(api))
    else:
        print("Unknown argument")
