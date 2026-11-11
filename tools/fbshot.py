# c.py로 상태 저장 후 표시 중인 프레임버퍼를 3배 확대 저장
import subprocess,sys,os,time,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import fb
from PIL import Image
subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'c.py'),'k f2'],capture_output=True); time.sleep(3)
out=fb.vram(); b=fb.base(out)
v=np.frombuffer(out[b:b+1048576],'<u2').reshape(512,1024)
ims=[]
for y0 in (0,240):
    c=v[y0:y0+240,0:320]; ims.append(np.dstack([(c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3]).astype('uint8'))
# 두 버퍼 중 최근 것: 그냥 둘 다 가로로
im=Image.fromarray(np.hstack(ims)); im.resize((im.width*int(sys.argv[2]) if len(sys.argv)>2 else im.width*2, im.height*(int(sys.argv[2]) if len(sys.argv)>2 else 2)),0).save(sys.argv[1])
