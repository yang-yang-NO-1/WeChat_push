fork了下别人的代码，添加了一小部分人性化的提醒
（大致了解了下github action执行过程，yaml类似于linux的bash，挨个执行的）
如果想加其他，后续再添加：dongdong留

底下是别人的readme，常用的链接我放出来：
和风天气api的key：https://id.qweather.com/#/homepage
（和风还有各种api口，有需要可以看）
微信推送的服务程序沙盒：https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index
别人的教程：
https://www.coolapk.com/feed/38579891?shareKey=NGI3ZGZlZTM4MDBjNjMwMzdlM2M~&shareUid=3198334&shareFrom=com.coolapk.app_4.10

yml文件中改定时时间

🔺模板内容如下：🔺
(这个可以自由发挥，只要保证传给tx的data中有该key，腾讯平台中，设置标题和模版(底下)，模版中有key就可以)
----------------------------------------------------------------------------------------------------------------------------------
{{date.DATA}} 

地区：{{region.DATA}} 

天气：{{weather.DATA}} 

气温：{{temp.DATA}} 

风向：{{wind_dir.DATA}} 

今天是我们恋爱的第{{love_day.DATA}}天 

{{birthday1.DATA}} 

{{birthday2.DATA}}

{{note_en.DATA}} 

{{note_ch.DATA}}
----------------------------------------------------------------------------------------------------------------------------------

