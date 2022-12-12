## 南京邮电大学 企业微信 自动健康打卡

## 哦吼，停止打卡了，没啥用了啊

### 本脚本支持所有在 工作台-健康打卡 中打卡的企业微信

## 食用方法

### 有`Python3`环境的用户:

0. 给我点个`star`, 前往[release](https://github.com/FishZe/WXWork-HealthReport/releases)下载`HealthReport.zip`文件, 并解压
   
1. 登录**电脑版**企业微信, 打开抓包工具(如`Charles`, 需要安装证书, 自行上网查阅资料), 在企业微信中打开**工作台-健康上报**, 抓包, 寻找`https://work.weixin.qq.com/healthreport/share`的请求, 并将请求头的`Cookies`中的相关值填入`json/cookies.json`中, 保存
   
2. 安装相关依赖
   ```bash
    pip install -r requirements.txt
    ```
   
3. `python3 main.py`即可，根据提示设置好答案, 程序会定时打卡
   
### 无`Python3`环境的用户:

1. 给我点个`star`, 前往[release](https://github.com/FishZe/WXWork-HealthReport/releases)下载`main.exe`(`Windows amd64`)或`main`(`Linux amd64`)文件, 并解压

2. 运行`main.exe`或`main`, 注意`windows`用户双击运行后会生成`.bat`文件, 请再次双击运行`.bat`文件, `linux`用户请在终端中运行`./main`

3. 在生成的`json`文件夹中, 打开`cookies.json`文件, 将`cookies`中的相关值填入`json/cookies.json`中, 保存 (参考上面的方法)

4. 根据提示填好答案并保持运行即可 

### **注意: 企业版微信不可以点退出登录, 只可以从右下角右键退出, 否则可能会失效**

### TODO:
1. 找到更好的获取`cookies`和保活的方法，希望有大佬可以提出`Issue`
2. 支持更多的通知方式, 包括但不限于QQ机器人/企业微信推送等等
   
