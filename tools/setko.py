import glob,sys
def setko(R):
    R=dict(R)
    for f in glob.glob('text/ko_*.tsv'):
        L=open(f,encoding='utf-8').read().split('\n'); out=[]
        for l in L:
            p=l.split('\t')
            if len(p)==3 and (p[0],int(p[1])) in R: p[2]=R.pop((p[0],int(p[1])))
            out.append('\t'.join(p))
        open(f,'w',encoding='utf-8').write('\n'.join(out))
    assert not R,R
