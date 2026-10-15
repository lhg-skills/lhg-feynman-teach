import json
from PIL import Image,ImageDraw,ImageFont
from script import BEATS
import os
HW=os.environ['HW_FONT']; SC=os.environ['SC_FONT']; SC_INDEX=int(os.environ.get('SC_INDEX','0'))
PAPER='#FAF6EC'; INK='#22262E'; CORAL='#E8735A'; TEAL='#2F8F8F'; YEL='#F2C94C'
# cover
c=Image.new('RGB',(1920,1080),PAPER); d=ImageDraw.Draw(c)
art=Image.open('inputs/desk.png').convert('RGB'); art=art.resize((1000,int(1000*art.height/art.width)))
from PIL import ImageChops
bg=Image.new('RGB',art.size,PAPER); c.paste(ImageChops.multiply(art,bg),(860,170))
d.rectangle((110,380,780,430),fill=YEL)
f=ImageFont.truetype(HW,120); d.text((110,200),'AI 答对了，',font=f,fill=INK); d.text((110,330),'就算学会了吗？',font=f,fill=INK)
d.text((115,560),'费曼教学 | 30 秒',font=ImageFont.truetype(HW,56),fill=TEAL)
d.text((115,900),'刘洪光 出品',font=ImageFont.truetype(SC,34,index=SC_INDEX),fill='#6B6B6B')
c.save('inputs/cover.png')
rest=[[0,0],[1,0],[1,1],[0,1]]
def R(x0,y0,x1,y1): return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
def T(t,x,y,s,col=INK,w=1): return {"type":"text","text":t,"x":x,"y":y,"size":s,"color":col}
ill=lambda src,x,y,w,h,parts,wt: {"type":"illustration","source":src,"x":x,"y":y,"width":w,"height":h,"weight":wt,"parts":[{"id":i,"polygon":p} for i,p in parts]}
desk=[("head",R(.24,.13,.38,.33)),("torso_arms",R(.22,.32,.50,.70)),("lower_body_chair",R(.27,.52,.72,.92)),("desk_laptop_robot",rest)]
sa=[("head",R(.18,.10,.48,.36)),("left_arm",[[.02,.27],[.21,.27],[.25,.63],[.07,.63]]),("torso_right_arm",R(.10,.34,.70,.72)),("lower_body",R(.15,.64,.52,.90)),("whiteboard",rest)]
sb=[("head",R(.26,.05,.47,.24)),("torso_arms_paper",R(.18,.22,.62,.56)),("lower_body",R(.22,.54,.56,.96)),("robot",rest)]
tk=[("adult_head",R(.32,.07,.45,.23)),("adult_body",R(.18,.17,.55,.92)),("child_head_bulb",R(.60,.20,.75,.50)),("child_body",R(.50,.48,.75,.86)),("laptop",rest)]
acts={
"hook":[T('AI 答对了，',110,150,112),T('就算学会了吗？',110,290,112),{"type":"marker","style":"highlight","x":104,"y":370,"width":690,"height":40,"color":YEL}],
"forum":[ill('inputs/desk.png',840,150,1020,684,desk,3),T('10月11日 清华',115,560,64,TEAL),T('AI 与数学论坛的一道题',115,660,58,TEAL)],
"ab":[ill('inputs/student-a.png',40,150,460,571,sa,3),T('学生 Ａ',520,200,84,TEAL),T('八成靠 AI',520,320,56),T('讲得清清楚楚',520,400,56),
      ill('inputs/student-b.png',1000,150,460,571,sb,3),T('学生 Ｂ',1480,200,84,CORAL),T('答案全对',1480,320,56),T('只是照搬 AI',1480,400,56)],
"verdict":[{"type":"marker","style":"box","x":495,"y":180,"width":420,"height":300,"color":TEAL,"line_width":7},
           T('答案对，不等于真懂',560,790,92,INK),{"type":"marker","style":"underline","x":555,"y":905,"width":830,"height":24,"color":CORAL,"line_width":9}],
"feynman":[ill('inputs/teach-kid.png',800,130,1060,710,tk,3),T('合上 AI',120,190,104),T('讲给 12 岁',120,340,104),T('孩子听',120,490,104)],
"close":[T('讲得出来，才算你的。',120,690,84,CORAL),{"type":"marker","style":"highlight","x":112,"y":770,"width":760,"height":34,"color":YEL}]}
pages=[["hook","forum"],["ab","verdict"],["feynman","close"]]
txt=dict(BEATS)
job={"version":1,"runtime_fixture":True,"title":"AI答对了，就算学会了吗","paper":PAPER,
 "canvas":{"width":1920,"height":1080,"fps":30},"cover":{"source":"inputs/cover.png","seconds":1.0},
 "hand":{"preset":"teacher-pen","pen_text":"费曼教学"},
 "font":{"path":HW,"index":0},
 "narration":{"source":"inputs/narration/master.wav","alignment":"inputs/narration/alignment.json"},
 "audio":{"end_hold_seconds":0.6},"ending":{"fade_seconds":0.4},
 "captions":{"font":{"path":SC,"index":SC_INDEX},"font_size":44,"color":"#FFFFFF","stroke_width":0,"bottom_margin":38,"max_width_ratio":0.9,"max_lines":1,"background":{"color":"#243039","opacity":0.78}},
 "pages":[{"beats":[{"id":b,"text":txt[b],"actions":acts[b]} for b in p]} for p in pages]}
al={b['id']:b for b in json.load(open('inputs/narration/alignment.json'))['beats']}
for p in job['pages']:
    for b in p['beats']: b['caption_cues']=al[b['id']]['caption_cues']
json.dump(job,open('job.json','w'),ensure_ascii=False,indent=1)
