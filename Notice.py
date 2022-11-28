class Notice:
    def __init__(self):
        pass

    def notice(self, type, title, msg):
        colors = {"error": "[31m", "success": "[32m", "warning": "[33m", "info": "[34m"}
        if type not in colors.keys():
            type = "info"
        print("\033%s%-10s%s: %s\033[0m" % (colors[type], f"[{type}]", title, msg))

