# RetroArch 상주 제어 서버: python srv.py <cue> [state] / 클라이언트: python c.py "명령;명령"
import sys,os,socket,time,traceback,shutil
sys.path.insert(0,os.path.dirname(__file__))
from emu import Emu
e=Emu(os.path.abspath(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else None)
s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',2399));s.listen(1)
while True:
    c,_=s.accept();cmd=c.recv(65536).decode();out=''
    try:
        for part in cmd.split(';'):
            a=part.split()
            if not a: continue
            if a[0]=='p':
                for k in a[1:]:
                    if k[0]=='w': time.sleep(float(k[1:]))
                    else: e.key(k,0.12); time.sleep(0.35)
            elif a[0]=='k': e.key(a[1],float(a[2]) if len(a)>2 else 0.15)
            elif a[0]=='pb':
                B={'select':(0,0),'start':(0,3),'up':(0,4),'right':(0,5),'down':(0,6),'left':(0,7),'l2':(1,0),'r2':(1,1),'l1':(1,2),'r1':(1,3),'tri':(1,4),'o':(1,5),'x':(1,6),'sq':(1,7)}
                b=[0xff,0xff]; i,j=B[a[1]]; b[i]&=~(1<<j)&0xff
                t=time.time()+(float(a[2]) if len(a)>2 else 0.15)
                while time.time()<t: e.write(0x801c7c9a,bytes(b))
                t=time.time()+0.12
                while time.time()<t: e.write(0x801c7c9a,bytes([255,255]))
            elif a[0]=='kd': e.kev(a[1],0)
            elif a[0]=='ku': e.kev(a[1],1)
            elif a[0]=='w': time.sleep(float(a[1]))
            elif a[0]=='grab': out+=str(e.grab(os.path.abspath(a[1])))+chr(10)
            elif a[0]=='shot': out+=str(e.shot(os.path.abspath(a[1])))+'\n'
            elif a[0]=='dump': open(a[1],'wb').write(e.read(0x80000000,0x200000)); out+='dumped'+chr(10)
            elif a[0]=='ss': e.key('f1')
            elif a[0]=='rd': out+=e.read(int(a[1],16),int(a[2],16)).hex()+'\n'
            elif a[0]=='wr': e.write(int(a[1],16),bytes.fromhex(a[2]))
            elif a[0]=='ff': e.key('tab',float(a[1]) if len(a)>1 else 1)
            elif a[0]=='save': out+=str(e.save(os.path.abspath(a[1])))+'\n'
            elif a[0]=='kp':
                # 확실한 입력: 패드 버퍼에 눌림이 보일 때까지 keydown 재전송
                for _ in range(8):
                    e.kev(a[1],0); time.sleep(0.12)
                    if e.read(0x800a93a6,2)!=b'\xff\xff': break
                time.sleep(0.08); e.kev(a[1],1); time.sleep(0.25)
            elif a[0]=='regs':
                e.halt(); out+=e.cmd('g')+chr(10); e.cont()
            elif a[0]=='bp':
                e.halt(); e.cmd('Z0,%s,4'%a[1]); e.cont()
            elif a[0]=='bw':
                e.sock.settimeout(float(a[1]))
                try:
                    r=e._recv(); e.sock.settimeout(None); out+='STOP '+str(r)+chr(10)+e.cmd('g')+chr(10)
                    if len(a)>2: out+=e.cmd('m%s,100'%a[2])+chr(10)
                except Exception as ex:
                    e.sock.settimeout(None); out+='timeout'+chr(10); e.halt()
                e.cmd('z0,%s,4'%a[3] if len(a)>3 else 'z0,80010000,4'); e.cont()
            elif a[0]=='raw':
                e.halt(); out+=e.cmd(a[1])+chr(10); e.cont()
            elif a[0]=='wst':
                e.sock.settimeout(float(a[1]))
                try:
                    r=e._recv(); e.sock.settimeout(None); out+='STOP '+str(r)+chr(10)+e.cmd('g')+chr(10)
                except Exception:
                    e.sock.settimeout(None); out+='timeout'+chr(10); e.halt()
                for z in a[2:]: out+=e.cmd(z)+chr(10)
                e.cont()
            elif a[0]=='excw':
                # 예외 벡터에서 인터럽트가 아닌 예외만 포착
                import struct,binascii
                e.halt(); e.cmd('Z1,80000080,4'); e.cont()
                if len(a)>2: e.key(a[2],0.12)
                t_end=time.time()+float(a[1]); got=None
                e.sock.settimeout(2)
                while time.time()<t_end:
                    try: e._recv()
                    except Exception: continue
                    g=e.cmd('g'); w=struct.unpack('<38I',binascii.unhexlify(g[:38*8]))
                    if ((w[36]>>2)&31) in (4,5,6,7,10,11,12): got=g; break
                    e.sock.sendall(b'$c#63')
                e.sock.settimeout(None)
                if got is None: e.halt()
                out+=(got or 'none')+chr(10)
                if got:
                    for z in ('m%x,40'%(w[31]-0x20),): out+=e.cmd(z)+chr(10)
                e.cmd('z1,80000080,4'); e.cont()
            elif a[0]=='trace':
                # trace addr n reg_index [key...]: bp에서 레지스터 기록
                import struct,binascii
                ad=a[1]; n=int(a[2]); ri=int(a[3])
                e.halt(); e.cmd('Z0,%s,4'%ad); e.cont()
                for k in a[4:]: e.key(k,0.12); time.sleep(0.4)
                e.sock.settimeout(5); seen=[]
                for _ in range(n):
                    try: e._recv()
                    except Exception: break
                    g=e.cmd('g'); w=struct.unpack('<38I',binascii.unhexlify(g[:38*8]))
                    seen.append('%08x:%08x'%(w[ri],w[31]))
                    e.sock.sendall(b'$c#63')
                e.sock.settimeout(None); e.halt(); e.cmd('z0,%s,4'%ad); e.cont()
                out+=' '.join(seen)+chr(10)
            elif a[0]=='rehwnd': e.hwnds=e._find(); out+=str(e.hwnds)+chr(10)
            elif a[0]=='quit': e.close(); c.sendall(b'bye'); c.close(); sys.exit()
    except Exception: out+=traceback.format_exc()
    try: c.sendall(out.encode() or b'ok');c.close()
    except OSError: pass
