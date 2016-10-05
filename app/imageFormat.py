# -*- coding: UTF-8 -*-
from PIL import Image

import os,sys,hashlib

imageSize = [200,100,24]

def resizeImage(image,md5):
    for size in imageSize:
        _image = Image.open(image)
        _image.resize((size,size),Image.ANTIALIAS).save('C:\\Users\\vanshin\\Documents\\Code\\flask.com\\app\\static\\pic\%s_%d.jpg'%(md5,size))

def CalcMD5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash
