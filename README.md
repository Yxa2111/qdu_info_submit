# qdu_info_submit

QDU校园集结号每日上报+github action，利用后者实现自动化

inspired by [@kxkxk](https://github.com/kxkxk), thanks a lot!

some of api request is based on [antlinkercampus](https://github.com/jj4/antlinkercampus).

# Please keep slience!🤐

# How to use ?

1. 注册你的Github账号
2. 点击首页的加号，选择`Import Repository`，clone URL填`https://github.com/Yxa2111/qdu_info_submit.git`，名字随意，然后设置为private。

3. 进入新导入的repo，选择Settings -- Actions，选择`Allow all actions`然后Save。

![](imgs/open_action.png)

4. 在刚刚的Settings里，点击Scrects，然后点击右边的`New Repository Screct`按钮，添加一个新的screct。Name中填`PHONE`，Value中填你的`your phone number here which registered 校园集结号`

5. 遵循上面的步骤，分别填写Name为`PASSWORD`，Value为`your password`的screct和Name为`KEYWORD`，Value为`体温`的screct。

5. enjoy it! 你可以随便push一个commit来触发action，或者点击右上角的`star`来触发，看下结果如何。之后的运行结果可以在Actions里看到，每天大概四小时运行一次。

# Extra: 邮件通知

进入`https://github.com/settings/notifications`，然后在Action里取消勾选`Send notifications for failed workflows only`
