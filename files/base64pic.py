#-*- coding: UTF-8 -*-
import win32ui
import os
import base64
import pyperclip
from PIL import ImageGrab
from PIL import Image
import datetime

im = ImageGrab.grabclipboard()
if isinstance(im, Image.Image):
    img = im
else:
    dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
    dlg.SetOFNInitialDir('C:\\Users\\0049001237\\Pictures')  # 设置打开文件对话框中的初始显示目录
    dlg.DoModal()
    filename = dlg.GetPathName()  # 获取选择的文件名称
    img = Image.open(filename)  

x,y=img.size    
#img.thumbnail((x/2,y/2), Image.ANTIALIAS)
img=img.convert('RGB')
img.save("C:\\Users\\0049001237\\Pictures\\1.jpg", quality=90)
now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
with open("C:\\Users\\0049001237\\Pictures\\1.jpg", 'rb') as f:
    base64_data = base64.b64encode(f.read())
    im_data = base64_data.decode()
    #print('![](data:image/jpeg;base64,%s)'%s)
    pyperclip.copy('![image][%s] [%s]:data:image/jpeg;base64,%s'%(now_time,now_time,im_data))
os.remove("C:\\Users\\0049001237\\Pictures\\1.jpg")