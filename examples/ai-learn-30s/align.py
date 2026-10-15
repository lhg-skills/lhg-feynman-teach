import json,hashlib,re
from script import BEATS
W=[m for m in json.load(open('work/boundaries.json')) if m['t']=='WordBoundary']
full="".join(t for _,t in BEATS)
# map every non-punct char of full text to a time via word boundaries
times=[None]*len(full); pos=0
for w in W:
    i=full.find(w['text'],pos); assert i>=0,(w,pos)
    n=len(w['text'])
    for k in range(n): times[i+k]=(w['start']+(w['end']-w['start'])*k/n, w['start']+(w['end']-w['start'])*(k+1)/n)
    pos=i+n
def span(a,b):
    ts=[times[k] for k in range(a,b) if times[k]]; return ts[0][0],ts[-1][1]
out=[];off=0
for bid,t in BEATS:
    s,e=span(off,off+len(t)); s=max(0,s-0.08); e=e+0.12
    cues=[];parts=re.findall(r'[^，。；：？]+[，。；：？]?',t);co=off
    # merge tiny clauses so each cue is 6-18 chars
    merged=[]
    for p in parts:
        if merged and (len(merged[-1])<6 or len(merged[-1])+len(p)<=12): merged[-1]+=p
        else: merged.append(p)
    assert "".join(merged)==t
    for p in merged:
        cs,ce=span(co,co+len(p)); cues.append({"text":p,"start":round(max(0,cs-s-0.04),3),"end":round(ce-s+0.1,3)}); co+=len(p)
    for a,b in zip(cues,cues[1:]): a['end']=min(a['end'],b['start'])
    out.append({"id":bid,"text":t,"start":round(s,3),"end":round(e,3),"caption_cues":cues}); off+=len(t)
for a,b in zip(out,out[1:]):
    if a['end']>b['start']: a['end']=b['start']-0.01
src=hashlib.sha256(open('inputs/narration/master.wav','rb').read()).hexdigest()
al={"version":1,"source_sha256":src,"script_sha256":hashlib.sha256(full.encode()).hexdigest(),"beats":out}
json.dump(al,open('inputs/narration/alignment.json','w'),ensure_ascii=False,indent=1)
for b in out: print(b['id'],b['start'],b['end'],[ (c['text'],c['start'],c['end']) for c in b['caption_cues']])
