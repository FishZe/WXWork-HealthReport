class Notice:
    def __init__(self):
        pass

    # TODO: 添加更多的通知方式 增加事件绑定
    def notice(self, types, title, msg):
        colors = {"error": "[31m", "success": "[32m", "warning": "[33m", "info": "[34m"}
        if type not in colors.keys():
            types = "info"
        print("\033%s%-10s%s: %s\033[0m" % (colors[types], f"[{types}]", title, msg))

