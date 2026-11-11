# 타입 0 원시 VRAM 이미지(4bpp 인덱스) 편집 도구
import struct,os,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
def load(fad,a):
    x,y,w,h=struct.unpack_from('<4H',fad,a)
    d=np.frombuffer(bytes(fad[a+8:a+8+w*h*2]),np.uint8).reshape(h,w*2)
    img=np.empty((h,w*4),np.uint8); img[:,0::2]=d&15; img[:,1::2]=d>>4
    return img
def store(fad,a,img):
    x,y,w,h=struct.unpack_from('<4H',fad,a)
    d=(img[:,0::2]&15)|((img[:,1::2]&15)<<4)
    fad[a+8:a+8+w*h*2]=d.astype(np.uint8).tobytes()
def boxes(img,region,dx=5,dy=1,minpx=8):
    x0,y0,x1,y1=region
    m=img[y0:y1,x0:x1]>0
    md=ndimage.binary_dilation(m,np.ones((2*dy+1,2*dx+1)))
    lab,n=ndimage.label(md)
    out=[]
    for sl in ndimage.find_objects(lab):
        ys,xs=sl
        sub=m[ys,xs]
        if sub.sum()<minpx: continue
        yy,xx=np.nonzero(sub)
        out.append((x0+xs.start+xx.min(),y0+ys.start+yy.min(),x0+xs.start+xx.max()+1,y0+ys.start+yy.max()+1))
    return sorted(out,key=lambda b:(b[1]//6,b[0]))
def render(text,font,size,box,lo=4,hi=15,outline=3,stretch=True,align='c',shadow=None):
    """box 안에 글자를 그려 (인덱스 배열, 마스크) 반환"""
    x0,y0,x1,y1=box; W=x1-x0; H=y1-y0
    F=ImageFont.truetype(font,size)
    S=4
    bb=F.getbbox(text)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    big=Image.new('L',(tw*S//1+8,th+8),0)
    F2=ImageFont.truetype(font,size*S)
    bb2=F2.getbbox(text)
    big=Image.new('L',(bb2[2]-bb2[0]+8,bb2[3]-bb2[1]+8),0)
    ImageDraw.Draw(big).text((4-bb2[0],4-bb2[1]),text,font=F2,fill=255)
    ib=big.getbbox(); big=big.crop(ib)
    pad=1 if outline is not None else 0
    iw,ih=W-2*pad,H-2*pad
    tw=round(big.width*ih/big.height)
    if tw>iw or stretch is False:
        tw=min(tw,iw)
    sm=big.resize((max(1,tw),ih),Image.LANCZOS)
    a=np.array(sm).astype(float)/255
    out=np.zeros((H,W),np.int16)-1
    ox=pad+((iw-tw)//2 if align=='c' else 0 if align=='l' else iw-tw)
    ink=a>0.12
    vals=np.clip(np.round(lo+(hi-lo)*a),lo,hi)
    region=out[pad:pad+ih,ox:ox+tw]
    region[ink]=vals[ink]
    if outline is not None:
        m=out>=0
        ring=ndimage.binary_dilation(m,np.ones((3,3)))&~m
        out[ring]=outline
    return out
def paste(img,box,arr,clear=0):
    x0,y0,x1,y1=box
    if clear is not None: img[y0:y1,x0:x1]=clear
    sub=img[y0:y1,x0:x1]
    m=arr>=0; sub[m]=arr[m]
def preview(img,path,scale=3,boxes_=None):
    im=Image.fromarray((img*17).astype(np.uint8)).convert('RGB')
    if boxes_:
        d=ImageDraw.Draw(im)
        for i,b in enumerate(boxes_):
            d.rectangle((b[0]-1,b[1]-1,b[2],b[3]),outline=(255,0,0)); d.text((b[0],b[1]-1),str(i),fill=(0,255,0))
    im.resize((im.width*scale,im.height*scale),Image.NEAREST).save(path)
def words(img,region,gapx=6,thr=3):
    """행(가로 투영) → 열(간격) 단위로 단어 상자 검출"""
    x0,y0,x1,y1=region
    m=img[y0:y1,x0:x1]>thr
    rows=m.any(1); out=[]
    y=0
    while y<len(rows):
        if not rows[y]: y+=1; continue
        ys=y
        while y<len(rows) and rows[y]: y+=1
        ye=y
        cols=m[ys:ye].any(0); x=0
        while x<len(cols):
            if not cols[x]: x+=1; continue
            xs=x; last=x
            while x<len(cols) and (cols[x] or x-last<gapx):
                if cols[x]: last=x
                x+=1
            out.append((x0+xs,y0+ys,x0+last+1,y0+ye))
    return out
def show(img,region,bx,path,scale=3):
    x0,y0,x1,y1=region
    im=Image.fromarray((img*17).astype(np.uint8)).convert('RGB').crop(region).resize(((x1-x0)*scale,(y1-y0)*scale),Image.NEAREST)
    d=ImageDraw.Draw(im)
    for i,b in enumerate(bx):
        d.rectangle(((b[0]-x0)*scale,(b[1]-y0)*scale,(b[2]-x0)*scale-1,(b[3]-y0)*scale-1),outline=(255,0,0)); d.text(((b[0]-x0)*scale+2,(b[1]-y0)*scale),str(i),fill=(0,255,0))
    im.save(path)
