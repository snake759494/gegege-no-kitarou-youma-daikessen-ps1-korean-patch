# 거점 배경(8bpp, 팔레트가 밝기순)에 그려진 지명판 "鬼太郎の家" → "기타로의 집"
import struct,os,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
A=0xf2186c
GAP=(248,256)          # 그림 안의 빈 열: 화면에서는 오른쪽 부분이 8px 왼쪽으로 붙는다
X0,X1=196,322          # 판 가로 범위(텍스처)
TY0,TY1=212,224        # 글자 줄 범위
def apply(fad,text='기타로의 집'):
    x,y,w,h=struct.unpack_from('<4H',fad,A)
    I=np.frombuffer(bytes(fad[A+8:A+8+w*h*2]),np.uint8).reshape(h,w*2).copy()
    S=np.hstack([I[:,X0:GAP[0]],I[:,GAP[1]:X1]]).astype(float)
    c0,c1=20,92                         # 글자 열 범위(S 좌표)
    R=S[TY0:TY1,c0:c1]
    bg=ndimage.maximum_filter(ndimage.median_filter(S[TY0-1:TY1+1,c0-4:c1+4],size=(1,15)),size=(3,1))[1:-1,4:-4]
    m=R<bg*0.72
    m=ndimage.binary_dilation(m,np.ones((3,3)))
    # 행마다 마스크 밖 값으로 선형 보간
    for r in range(R.shape[0]):
        xs=np.arange(R.shape[1]); ok=~m[r]
        R[r,m[r]]=np.interp(xs[m[r]],xs[ok],R[r,ok])
    R[:]=ndimage.uniform_filter(R,size=(1,3))*m+R*~m
    # 글자
    F=ImageFont.truetype(os.path.join(W,'..','SeoulHangangEB.ttf'),44)
    bb=F.getbbox(text); g=Image.new('L',(bb[2]-bb[0]+8,bb[3]-bb[1]+8),0)
    ImageDraw.Draw(g).text((4-bb[0],4-bb[1]),text,font=F,fill=255); g=g.crop(g.getbbox())
    th=10; tw=60
    a=np.array(g.resize((tw,th),Image.LANCZOS)).astype(float)/255
    ox=c0+(c1-c0-tw)//2; oy=TY0+1
    sub=S[oy:oy+th,ox:ox+tw]; dark=0x18
    S[oy:oy+th,ox:ox+tw]=sub*(1-a)+dark*a
    S=np.clip(np.round(S),1,255).astype(np.uint8)
    n=GAP[0]-X0
    I[TY0-1:TY1+1,X0:GAP[0]]=S[TY0-1:TY1+1,:n]
    I[TY0-1:TY1+1,GAP[1]:X1]=S[TY0-1:TY1+1,n:]
    fad[A+8:A+8+w*h*2]=I.tobytes()
if __name__=='__main__':
    fad=bytearray(open(os.path.join(W,'orig/DATA.FAD'),'rb').read()); apply(fad)
    x,y,w,h=struct.unpack_from('<4H',fad,A)
    I=np.frombuffer(bytes(fad[A+8:A+8+w*h*2]),np.uint8).reshape(h,w*2)
    S=np.hstack([I[200:236,180:GAP[0]],I[200:236,GAP[1]:330]])
    Image.fromarray(S).resize((S.shape[1]*6,216),0).save(os.path.join(W,'zl2.png'))
