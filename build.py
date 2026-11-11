# 게게게의 기타로 역습! 요마대혈전 (SLPM-87286) 한글패치 빌드
import os, sys, json, struct, shutil
from PIL import Image, ImageDraw, ImageFont
import keystone
W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(W, 'tools'))
from fad import packs
from ko import load, width, N1, N2
from disc import Writer

SRC = os.path.join(W, '..', 'GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan).bin')
OUT = os.path.join(W, '..', 'GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan) [KR].bin')
log = open(os.path.join(W, 'build.log'), 'w', encoding='utf-8')
def warn(*a):
    print(*a, file=log)

fad = bytearray(open(os.path.join(W, 'orig/DATA.FAD'), 'rb').read())
exe = bytearray(open(os.path.join(W, 'orig/SLPM_872.86'), 'rb').read())
B = json.load(open(os.path.join(W, 'text/ja.json'), encoding='utf-8'))
ko = load()

# ---------- 글자 목록 ----------
FULL, HALF = '　', ' '
used = set(''.join(ko.values()))
chars = [c for c in N1 if c in used or c == HALF]
K1 = len(chars)
chars += [c for c in N2 if c in used]
K2 = len(chars)
chars.append(FULL)
for k in sorted(ko):
    for c in ko[k]:
        if c != '/' and c not in chars:
            chars.append(c)
assert chars[0] == HALF
FONT_OFF, FONT_CAP = 0x19858, 0xb130          # 팩0 엔트리3 (type 0x12) → RAM 0x8019F800
TBL_OFF, TBL_CAP = 0x24988, 0x25000 - 0x24988  # 팩0 엔트리4 (type 0x13) → RAM 0x8001F000
assert len(chars) * 72 <= FONT_CAP, ('글자 수 초과', len(chars))
TRAILS = [t for t in range(0x40, 0xfd) if t != 0x7f]
def code(i):
    if i == 0:
        return b'\x81\x40'
    i -= 1
    return bytes([0x88 + i // len(TRAILS), TRAILS[i % len(TRAILS)]])
CODE = {c: code(i) for i, c in enumerate(chars)}
print('글자 수', len(chars), file=log)

# ---------- 글꼴 ----------
gal = ImageFont.truetype(os.path.join(W, 'fonts/Galmuri11.ttf'), 12)
def glyph(c):
    im = Image.new('L', (12, 12), 0)
    if c not in (FULL, HALF):
        ImageDraw.Draw(im).text((7 if c == '【' else 0, -1), c, font=gal, fill=255)
    px = im.load(); out = bytearray(72)
    for y in range(12):
        for x in range(12):
            v = 14 if px[x, y] >= 128 else 0
            o = (y * 12 + x) // 2
            out[o] |= (v << 4) if x & 1 else v
    return bytes(out)
font = b''.join(glyph(c) for c in chars)
fad[FONT_OFF:FONT_OFF + FONT_CAP] = font.ljust(FONT_CAP, b'\0')

# ---------- 문자표 + 반각 공백 처리 코드 ----------
tbl = b''.join(CODE[c] for c in chars) + b'\0\0'
tbl = tbl.ljust((len(tbl) + 3) & ~3, b'\0')
NEW = 0x8001F000 + len(tbl)
XV = 0x8001F000 + TBL_CAP - 4        # 현재 줄 x 위치(VRAM 단위) 저장
hi = (XV + 0x8000) >> 16; lo = XV & 0xffff
lo_s = lo - 0x10000 if lo >= 0x8000 else lo
asm = f'''.set noreorder
 addiu $sp,$sp,-0x28
 sw $ra,0x20($sp)
 lui $t0,{hi:#x}
 lhu $v0,{lo_s}($t0)
 bnez $a1,L1
 nop
 move $v0,$zero
L1:
 addiu $v1,$v0,0x200
 sh $v1,0x10($sp)
 sltiu $v1,$a0,{K1}
 bnez $v1,L2
 addiu $v1,$v0,1
 sltiu $v1,$a0,{K2}
 bnez $v1,L2
 addiu $v1,$v0,2
 addiu $v1,$v0,3
L2:
 sh $v1,{lo_s}($t0)
 sll $v0,$a2,1
 addu $v0,$v0,$a2
 sll $v0,$v0,2
 sll $a3,$a3,6
 addu $v0,$v0,$a3
 sh $v0,0x12($sp)
 addiu $v1,$zero,3
 sh $v1,0x14($sp)
 addiu $v0,$zero,0xc
 sh $v0,0x16($sp)
 andi $a0,$a0,0xffff
 sll $v0,$a0,3
 addu $v0,$v0,$a0
 sll $v0,$v0,3
 lui $a1,0x800f
 lw $a1,-0x6b2c($a1)
 nop
 addu $a1,$a1,$v0
 sw $a1,0x18($sp)
 jal 0x800d9044
 addiu $a0,$sp,0x10
 lw $ra,0x20($sp)
 nop
 jr $ra
 addiu $sp,$sp,0x28
'''
ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
enc, _ = ks.asm(asm, NEW)
code_bin = bytes(enc)
blob = tbl + code_bin
assert len(blob) <= TBL_CAP - 4, '문자표 영역 초과'
blob = blob.ljust(TBL_CAP, b'\0')
fad[TBL_OFF:TBL_OFF + TBL_CAP] = blob
struct.pack_into('<I', fad, 0x38, TBL_CAP)   # 팩0 엔트리4 크기
# 실행파일: 원래 글리프 전송 함수(0x80033794) → 새 함수로 점프
j, _ = ks.asm('.set noreorder; j %#x; nop' % NEW, 0x80033794)
eo = 0x80033794 - 0x80020000 + 0x800
exe[eo:eo + 8] = bytes(j)

# ---------- 대사 ----------
def enc_str(s, ja):
    # 가운데 정렬된 지명: 앞의 전각 공백 개수로 원래 중심 위치를 계산해 다시 맞춘다
    if ja.startswith('　' * 4) and '\n' not in ja and not s.startswith('　　　　　　'):
        k = len(ja) - len(ja.lstrip('　'))
        n = len(ja) - k
        body = s.lstrip('　')
        center = 12 * k + 6 * n
        pad = center - width(body) / 2
        best = min(((a, b) for a in range(0, 30) for b in range(0, 3)), key=lambda t: abs(12 * t[0] + 4 * t[1] - pad))
        s = '　' * best[0] + ' ' * best[1] + body
    out = bytearray()
    for c in s:
        out += b'\n\n' if c == '/' else CODE[c]
    return bytes(out)

def build_block(strs_ko, strs_ja):
    n = len(strs_ko)
    head = 4 * n; body = bytearray(); offs = []
    for s, ja in zip(strs_ko, strs_ja):
        offs.append(head + len(body))
        e = enc_str(s, ja) + b'\0\0'
        e = e.ljust((len(e) + 3) & ~3, b'\0')
        body += e
    return struct.pack('<%dI' % n, *offs) + bytes(body)

P = packs(bytes(fad))
pmap = {s: e for s, e in P}
for i, bl in enumerate(B):
    src = bl if 'strs' in bl else B[bl['dup']]
    ja = src['strs']
    ks_ = [ko[(B.index(src), j)] for j in range(len(ja))]
    for j, s in enumerate(ks_):
        for ln in s.split('/'):
            if width(ln) > 252:
                warn('너비 초과', i, j, ln)
    data = build_block(ks_, ja)
    # 팩 찾기
    s0 = max(s for s in pmap if s <= bl['abs'] and any(s + o == bl['abs'] for o, t, z in pmap[s]))
    ents = [list(x) for x in pmap[s0]]
    ei = next(k for k, (o, t, z) in enumerate(ents) if s0 + o == bl['abs'])
    o, t, z = ents[ei]
    end = ents[-1][0] + ents[-1][2]
    limit = ((s0 + end + 0x7ff) & ~0x7ff) - s0
    newlen = (len(data) + 3) & ~3
    data = data.ljust(newlen, b'\0')
    delta = newlen - z
    if end + max(delta, 0) > limit:
        raise SystemExit(f'B{i}: 팩 공간 부족 {end + delta:#x} > {limit:#x}')
    if delta <= 0:
        fad[s0 + o:s0 + o + z] = data.ljust(z, b'\0')
    else:
        tail = bytes(fad[s0 + o + z:s0 + end])
        fad[s0 + o:s0 + o + newlen] = data
        fad[s0 + o + newlen:s0 + o + newlen + len(tail)] = tail
        ents[ei][2] = newlen
        for k in range(ei + 1, len(ents)):
            ents[k][0] += delta
        if tail:
            warn(f'B{i}: 팩 {s0:#x} 엔트리 {ei} 확장 {delta:+#x}, 뒤 엔트리 이동')
    for k, (o2, t2, z2) in enumerate(ents):
        struct.pack_into('<3I', fad, s0 + 12 * k, o2, t2, z2)
    pmap[s0] = [tuple(x) for x in ents]
    print(f'B{i}: {z:#x} -> {newlen:#x}', file=log)

# ---------- 그림 글자 ----------
import gfxprev
gfxprev.apply(fad)
import logo8; logo8.apply(fad)
import bglabel; bglabel.apply(fad)

# ---------- 디스크 (바뀐 섹터만 다시 기록) ----------
shutil.copyfile(SRC, OUT)
w = Writer(OUT)
for path, new in (('/DATA.FAD', bytes(fad)), ('/SLPM_872.86', bytes(exe))):
    _, lba, size, _, _ = w.files[path]
    assert len(new) == size, (path, len(new), size)
    old = w.read(lba, size)
    for k in range(0, size, 2048):
        if old[k:k + 2048] != new[k:k + 2048]:
            w.wsec(lba + k // 2048, new[k:k + 2048], keep_sub=True)
w.f.close()
print('완료:', OUT, '글자', len(chars))
