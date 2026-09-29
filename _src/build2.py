"""Pathfinder Guidebook generator: builds home page, chapter openers, and lesson pages
from chapter config + lesson body fragments in bodies/chNN/."""
import re, pathlib
HERE = pathlib.Path(__file__).parent
ROOT = HERE.resolve().parent   # the site root (this folder's parent)
V = 27
BOOK = 'Pathfinder Guidebook'

def svg(path, sw='2', extra='', cls='ic'):
    c = f'class="{cls}" ' if cls else ''
    return f'<svg {c}viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{path}</svg>'

ICON = {
 'flag': svg('<path d="M4 21V4M4 4h12l-2 4 2 4H4"/>'),
 'home': svg('<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/>'),
 'menu': svg('<path d="M4 6h16M4 12h16M4 18h10"/>', '2.2'),
 'next': svg('<path d="M5 12h14M13 6l6 6-6 6"/>', '2.5'),
 'prev': svg('<path d="M19 12H5M11 6l-6 6 6 6"/>', '2.5'),
 'clock': svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
 'pen': svg('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>', cls=''),
}
RUBRIC = """          <table class="rubric">
            <caption class="sr-only">Mile Marker scoring guide</caption>
            <thead><tr><th scope="col">Score</th><th scope="col">What it means</th></tr></thead>
            <tbody>
              <tr><th scope="row"><span class="lvl">4</span>Strong Progress</th><td>Your response is thoughtful, specific, and clearly connected to the purpose of the Mile Marker. You show strong reflection, effort, and engagement with the topic.</td></tr>
              <tr><th scope="row"><span class="lvl">3</span>On Track</th><td>Your response addresses the main parts of the task and shows reflection and engagement. Some ideas could be explained in more detail or connected more clearly.</td></tr>
              <tr><th scope="row"><span class="lvl">2</span>Developing</th><td>Your response is partially complete or too general. More detail, reflection, or clearer connections are needed.</td></tr>
              <tr><th scope="row"><span class="lvl">1</span>Needs Revision</th><td>Your response is very limited, incomplete, or unclear and does not fully address the task.</td></tr>
              <tr><th scope="row"><span class="lvl">0</span>No Evidence</th><td>No submission was provided, or the response does not meaningfully engage with the task.</td></tr>
            </tbody>
          </table>"""
TOK = {
 'down': svg('<path d="M12 4v16M6 14l6 6 6-6"/>', '2.5', cls=''),
 'upload': svg('<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v4h16v-4"/>', cls=''),
 'download': svg('<path d="M12 4v12M7 11l5 5 5-5"/><path d="M4 20h16"/>', cls=''),
 'heart': svg('<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z"/>'),
 'term': svg('<path d="M6 3h12v18l-6-4-6 4Z"/>'),
 'tip': svg('<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5Z"/>'),
 'see': svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
 'pen': svg('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>'),
 'check': svg('<path d="m5 12 5 5 9-10"/>', '2.5'),
 'x': svg('<path d="M6 6l12 12M18 6 6 18"/>', '2.5'),
 'alert': svg('<path d="M12 3 2 20h20Z"/><path d="M12 10v4M12 17h.01"/>'),
 'tick': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>',
 'next': svg('<path d="M5 12h14M13 6l6 6-6 6"/>', '2.5', cls=''),
 'play': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7Z"/></svg>',
}
BE_ICON = {
 'Safe': svg('<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6Z"/>', cls=''),
 'Honest': svg('<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>', cls=''),
 'Critical': svg('<circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/>', cls=''),
 'Responsible': svg('<path d="M12 4v16M5 20h14M6 8h12M6 8l-3 6h6ZM18 8l-3 6h6Z"/>', cls=''),
 'Reflective': svg('<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>', cls=''),
}
ESSENTIAL = {1:'Communication',2:'Critical &amp; Creative Thinking',3:'Quantitative Reasoning',4:'Interpersonal Relations',
             5:'Adaptability &amp; Leadership',6:'Professionalism',7:'Civic Engagement',8:'Collaboration &amp; Teamwork',
             9:'Knowledge Application',10:'Information Literacy'}
FOCUS = {6, 9}
SPECIAL = {'Trail Tip', 'Trail Tool', 'Mile Marker', 'Wrap Up'}

# HARD RULE: every link that leaves the book opens in a new tab, with a screen-reader cue.
EXT = re.compile(r'<a\s+([^>]*?)href="(https?://[^"]+)"([^>]*)>(.*?)</a>', re.S)
def externalize(html):
    def fix(m):
        pre, url, post, inner = m.groups()
        attrs = re.sub(r'\s*(target|rel)="[^"]*"', '', pre + post).strip()
        attrs = (' ' + attrs) if attrs else ''
        return f'<a href="{url}"{attrs} target="_blank" rel="noopener">{inner}<span class="sr-only"> (opens in a new tab)</span></a>'
    out = EXT.sub(fix, html)
    for a in re.findall(r'<a\s[^>]*href="https?://[^>]*>', out):
        assert 'target="_blank"' in a, a
    return out

def write(path, html):
    # margin notes are supporting content, not page landmarks (keeps screen-reader landmark lists clean)
    html = html.replace('<aside class="note-col" aria-label="Margin notes">', '<div class="note-col">').replace('</aside>', '</div>')
    path.write_text(externalize(html))

def tokens(t):
    t = t.replace('[[rubric]]', RUBRIC)
    for k, v in TOK.items(): t = t.replace(f'[[{k}]]', v)
    assert '[[' not in t, t[t.index('[['):t.index('[[')+30]
    return t

# ------------------------------------------------------------------ chapters
CHAPTERS = [
 dict(n=1, title='Your Pathfinder Journey Begins',
  desc="Get oriented, set up your tools, and start thinking about why you're here and where you want to go.",
  tagline='Every journey starts with a single step, and this one is yours.',
  why=["Most students who struggle in college don't struggle because they aren't capable. They struggle because the rules changed and nobody told them: about expectations, about how to ask for help, about what it means to own your own learning.",
       "This module puts those things on the table early, while there's still time to build the right habits. What you set up here, including your goal, your sense of what college expects, and your first look at the skills and tools you'll use all semester, becomes the foundation for everything that follows."],
  objectives=[("describe my personal reasons for attending college and define what success means to me right now.", 'Mile Marker #1'),
              ("navigate Blackboard and locate key course information, assignments, and instructor contact details.", False),
              ("set one personal or academic goal for this semester and describe how I plan to reach it.", 'Mile Marker #1'),
              ("explain what artificial intelligence is and identify where it already shows up in my daily life.", False)],
  es=[1,5,6,10], be=['Safe'], be_note='This module also introduces all five BE behaviors you\'ll use throughout the book.',
  lessons=[
   ('1-1.html','1.1','College-Level Expectations',"The rules changed. Here's what nobody told you.",7,
     [('room',"Who's in this room"),('shift','The big shift'),('syllabus','The syllabus is a contract'),('expect','What instructors expect'),('own','Owning your learning')]),
   ('1-2.html','1.2','The 10 Essential Skills',"What Kentucky says every college graduate should be able to do, and where you're headed.",4,
     [('skills','The 10 skills'),('levels',"Where you're headed"),('growth','Tracking your growth')]),
   ('1-3.html','1.3',"What's AI, Really?","AI is already part of your daily life. This lesson is about using it thoughtfully.",5,
     [('patterns','The part that trips people up'),('be','Five ways to show up'),('yours','Your choice to make')]),
   ('1-4.html','1.4','Navigating AI Policies',"Every course sets its own AI rules. Here's how to find them, and a routine for using AI well.",6,
     [('find','Where to find the rules'),('unclear',"When rules aren't clear"),('three-qs','The 3 Qs'),('trail','Keep a trail'),('resource','Take it with you')]),
   ('1-5.html','1.5','Getting Around Blackboard Ultra',"The basics you need to navigate your courses with confidence.",5,
     [('profile','Set up your profile'),('around','Find your way around'),('submit','Submit your work'),('discuss','Take part in discussions'),('feedback','Read feedback'),('loop','Stay in the loop')]),
   ('trail-tip.html','Trail Tip','Your Free Office 365 Access',"As a KCTCS student, you already have the full Microsoft Office suite. Here's how to get it.",2,
     [('computer','PC or Mac'),('phone','Phone or tablet'),('included',"What's included")]),
   ('mile-marker.html','Mile Marker','Mile Marker #1: My Starting Point',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 1 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'1-3.html':'D','1-4.html':'D','1-5.html':'B','trail-tip.html':'B','mile-marker.html':'A, C'}),

 dict(n=2, title='Building Your Support System',
  desc='Map the people and resources around you, meet your Success Coach, and practice asking for help.',
  tagline='No one completes a journey alone. Every great Pathfinder relies on maps, tools, and traveling companions.',
  why=["College success isn't just about willpower. It's about knowing when and where to reach out. The students who struggle most aren't always the ones who don't know things. They're the ones who wait too long to ask.",
       "This module helps you build your support map: the people and resources you can actually use when things get hard. That network is one of the smartest investments you can make right now."],
  objectives=[("identify people and OCTC resources that can support my success and explain how each one helps.", 'Mile Marker #2'),
              ("describe how I will use my support system intentionally this semester.", 'Mile Marker #2'),
              ("identify one new campus resource I want to explore and explain why it matters for my goals.", 'Mile Marker #2'),
              ("practice asking for help clearly and specifically in a realistic college scenario.", True)],
  es=[1,4,9], be=['Honest','Responsible'], be_note='',
  lessons=[
   ('2-1.html','2.1','Skill Spotlight: Interpersonal Relations',"Interacting effectively with people, and understanding what you bring to every relationship.",5,
     [('what','What this skill is'),('headed',"Where you're headed"),('chapter','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('2-2.html','2.2',"Who's Your Success Coach?","Every Pathfinder needs a guide. Here's how to find yours.",3,
     [('find','Find your Success Coach'),('next','Next steps')]),
   ('2-3.html','2.3','Help-Seeking as a Strength',"Asking for help is a skill successful students use every day.",6,
     [('means','What help-seeking means'),('tips','Four tips'),('resources','OCTC support resources'),('notice','Pay attention to where you are')]),
   ('2-4.html','2.4','Professional Communication &amp; Email Etiquette',"Your KCTCS email is your lifeline. Here's how to use it well.",7,
     [('setup','Get to your email'),('write','Communicate professionally'),('examples','See the difference'),('check','Quick check')]),
   ('trail-tip-digital.html','Trail Tip','Set Up Your Digital Presence',"Two quick tasks that help you show up as a real person in a digital course.",5,
     [('email','Email on your phone'),('photo','Add a profile photo')]),
   ('trail-tip-merit.html','Trail Tip','Setting Up Your Merit Page',"Your Merit page is your official record of involvement and achievement at OCTC.",5,
     [('why-merit','What Merit does for you'),('setup','Set up your page'),('links','Helpful links')]),
   ('mile-marker.html','Mile Marker','Mile Marker #2: My Support Team',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 2 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'2-2.html':'A','2-3.html':'A, C, D','2-4.html':'D','mile-marker.html':'A, B, C'}),
 dict(n=3, title='My Time Plan — Managing Time &amp; Energy',
  desc="Track where your time actually goes, build a realistic weekly schedule, and manage your energy, not just your hours.",
  tagline="You have the same 168 hours as everyone else. This module is about figuring out where yours are actually going.",
  why=["Most students who struggle academically aren't lazy. They're overwhelmed, under-rested, and running on empty, and they don't realize it until things start falling apart.",
       "This module asks you to look honestly at where your time and energy are actually going: not the week you wish you had, but the one you actually live. That's the only honest starting point for building something better."],
  objectives=[("analyze how I currently spend my time and identify at least one pattern or time-waster.", 'Mile Marker #3'),
              ("create a realistic weekly schedule that reflects my actual priorities and commitments.", 'Mile Marker #3'),
              ("identify which of my five energy batteries needs the most attention and describe one way I will recharge it.", 'Mile Marker #3'),
              ("describe one small habit or adjustment I will make to manage my time more effectively.", 'Mile Marker #3')],
  es=[5,6], be=['Responsible'], be_note='',
  lessons=[
   ('where-my-time-goes.html','Trail Tool','Where My Time Goes',"Look back: an honest log of where your time and energy actually go.",5,
     [('how','How to log honestly'),('form','Fill in your log')]),
   ('my-week-at-a-glance.html','Trail Tool','My Week at a Glance',"Look ahead: plan from your priorities, not from empty boxes.",10,
     [('form','Plan your week')]),
   ('3-1.html','3.1','Skill Spotlight: Professionalism',"Being reliable, accountable, and intentional, not perfect.",5,
     [('what','What this skill is'),('headed',"Where you're headed"),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('3-2.html','3.2','Map Your Week',"Before the week runs you, run the week.",5,
     [('back-ahead','Look back, then ahead'),('steps','Three steps'),('mistakes','What gets in the way'),('start','Five minutes to start')]),
   ('3-3.html','3.3',"Run the Day (Don't Let It Run You)","Small, intentional decisions, made consistently, are how the day becomes yours.",7,
     [('moves','Four moves'),('real','What it sounds like'),('pilot',"You're the pilot")]),
   ('3-4.html','3.4','The Multitasking Myth',"You're not doing two things at once. You're switching really fast, and paying for it.",4,
     [('cost','The switching cost'),('familiar','Sound familiar?'),('friction','Transition friction')]),
   ('3-5.html','3.5','The Five Batteries: Running Low vs. Running Out',"Understanding your energy before it's gone, and what burnout actually is.",7,
     [('batteries','The five batteries'),('burnout','What burnout is'),('together',"They don't work alone"),('check-in','Check in with yourself')]),
   ('3-6.html','3.6','Your Brain, Your Way',"Some brains work differently. That's not a flaw, but it does matter.",9,
     [('means','What neurodivergence means'),('challenges','Executive function'),('strategies','Strategies'),('support','Support at OCTC')]),
   ('mile-marker.html','Mile Marker','Mile Marker #3: Managing My Time &amp; Energy',"The assignment, with support, and a form you can fill in and save.",12,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 3 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'where-my-time-goes.html':'A','3-2.html':'B','my-week-at-a-glance.html':'B','3-3.html':'A, D','3-4.html':'A, D','3-5.html':'C','3-6.html':'D','mile-marker.html':'A, B, C, D'}),
 dict(n=4, title='Your Academic Toolkit',
  desc="Study strategies grounded in how memory actually works, the SIFT method for evaluating information, and the tools you already have through Office 365.",
  tagline="The right tools make all the difference, but only if you know how to use them.",
  why=["You're surrounded by more information than any generation before you, and more of it is wrong, misleading, or designed to grab your attention rather than inform you.",
       "This module helps you build your academic toolkit: study strategies that actually work, a framework for evaluating what you read, and a direct look at where AI helps, and where it doesn't."],
  objectives=[("identify and apply at least one evidence-based study strategy and describe what I noticed about my learning.", 'Mile Marker #4'),
              ("evaluate a source or AI-generated response using the SIFT method and explain whether I would use it and why.", 'the AI Chat: Is This Legit?'),
              ("apply at least one digital organization strategy to manage my course files.", True),
              ("recognize AI creep in my own work and describe honestly how I used AI.", 'Mile Marker #4'),
              ("write one SMART goal for continuing a study strategy or academic habit this semester.", 'Mile Marker #4')],
  es=[6,10], be=['Honest','Critical','Responsible'], be_note='', merit=1,
  lessons=[
   ('trail-tip.html','Trail Tip','Your Office 365 Academic Toolkit',"You already have powerful tools. Here's how to use them for school.",5,
     [('onenote','OneNote'),('onedrive','OneDrive'),('teams','Teams'),('copilot','Copilot')]),
   ('4-1.html','4.1','Skill Spotlight: Information Literacy',"Finding, evaluating, and responsibly using information to make good decisions.",5,
     [('what','What this skill is'),('headed',"Where you're headed"),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('4-2.html','4.2','Study Strategies That Actually Work',"What the research says, and what to do with it.",8,
     [('strategies','Four strategies'),('myths',"What feels productive but isn't"),('smart','Write a SMART goal'),('ai-study','AI as a study partner')]),
   ('4-3.html','4.3','SIFT: Stop Before You Scroll',"Four moves for evaluating any information, including what AI tells you.",9,
     [('moves','The four moves'),('sift-ai','SIFT and AI'),('practice','Practice it')]),
   ('4-4.html','4.4','AI Literacy: Beware of the Creep',"Did you cross the line, and did you notice?",6,
     [('meter','The AI Creep Meter'),('boundary','Set your boundary'),('honest','BE Honest'),('attribution','Attribution'),('before','Before you submit')]),
   ('trail-tip-recording.html','Trail Tip','Recording in the Classroom',"Technology made recording easy. That doesn't make it automatic.",6,
     [('principles','Three principles'),('ai-notetakers','AI note-takers')]),
   ('mile-marker.html','Mile Marker','Mile Marker #4: My Academic Toolkit',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 4 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'trail-tip.html':'C','4-2.html':'A, E','4-3.html':'B','4-4.html':'D','mile-marker.html':'A, D, E'}),
]
LATER = [
 (5,"Financial Planning with Purpose","Build a zero-based budget, look honestly at your spending patterns, and explore what financial wellness means for your overall wellbeing."),
 (6,"Map Your Path — Academic Planning","Explore your interests, learn the difference between certificates, diplomas, and degrees, and prepare the questions you'll bring to your Success Coach."),
 (7,"Knowing Your Strengths &amp; Values","Discover your top strengths and personal values, and connect them to your academic habits and career direction."),
 (8,"Explore Your Career Options","Research a career, then honestly evaluate whether it fits your strengths, values, and work style."),
 (9,"Think It Through — Critical Thinking + STAR(T) Introduction","Build your critical thinking toolkit with the 4C Check, and meet the STAR(T) framework for telling your story."),
 (10,"Team Up — Collaboration &amp; People Skills","Explore how you work with others, name your collaboration strengths and challenges, and figure out what you need from a team."),
 (11,"Making an Impact — Community, Values &amp; Your Pathfinder Journey","See how communities work, and connect your strengths and values to how you want to show up in them."),
 (12,"Reflecting Back, Moving Forward","Look back at how far you've come, gather your evidence, and decide what you're taking with you."),
]

# ------------------------------------------------------------------ shared parts
def head(title, depth):
    up = '../'*depth
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="{up}css/styles.css?v={V}">
<script src="{up}js/book.js?v={V}" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''

def bookbar(depth, where):
    up = '../'*depth
    logo = f'<img class="logo logo-full" src="{up}images/shared/owensboro-logo-horizontal-gold.png" alt="Owensboro Community &amp; Technical College" width="716" height="120">'
    w = f'\n        <span class="where">{where}</span>' if where else ''
    return f'''
<header class="bookbar">
  <div class="inner">
    <a class="brand" href="{up}index.html" aria-label="{BOOK} home">
      {logo}
      <span class="brand-text">
        <span class="book">{BOOK}<span class="long"> · FYE 100</span></span>{w}
      </span>
    </a>
    <a class="contents-btn" href="{up}index.html#contents">{ICON['menu']}<span><span class="long">Book </span>Contents</span></a>
  </div>
</header>
'''

FOOT = '''
<footer>
  <div class="inner">
    <span>FYE 100: Strategies for College Success</span>
    <span>Owensboro Community &amp; Technical College</span>
  </div>
</footer>
</body>
</html>
'''

def banner_svg(label=''):
    w = 52 if len(label) <= 2 else 16 + 10.5 * len(label)
    fs = 16 if len(label) <= 2 else 15
    sign = f'''
    <g transform="translate(930 72)">
      <rect x="-3" y="0" width="6" height="42" fill="#eaf4fb"/>
      <rect x="{-w/2:.0f}" y="-6" width="{w:.0f}" height="26" rx="4" fill="#3bb3e5"/>
      <text x="0" y="13" text-anchor="middle" font-family="Aptos, Calibri, Arial, sans-serif" font-weight="800" font-size="{fs}" letter-spacing="1" fill="#011d41">{label}</text>
    </g>'''
    return f'''<svg class="banner-art" viewBox="0 -70 1200 240" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
    <circle cx="985" cy="58" r="80" fill="#e7a614"/>
    <path d="M0 120 L140 60 L250 105 L380 40 L520 110 L640 70 L760 115 L900 50 L1040 105 L1200 65 L1200 170 L0 170 Z" fill="#00467f" opacity=".85"/>
    <path d="M0 150 L180 100 L330 140 L470 95 L620 145 L800 105 L980 150 L1120 110 L1200 130 L1200 170 L0 170 Z" fill="#011d41"/>
    <path d="M120 170 C 300 150, 420 150, 560 140 S 820 120, 930 110" fill="none" stroke="#3bb3e5" stroke-width="4" stroke-dasharray="10 10" stroke-linecap="round"/>{sign}
  </svg>'''

def pages_of(ch):
    return [('index.html','Module overview')] + [(l[0], l[2] if l[1] in SPECIAL else f'{l[1]} {l[2]}') for l in ch['lessons']]

def sidebar(ch, current):
    n = ch['n']; items = []
    cur = ' aria-current="page"' if current=='index.html' else ''
    items.append(f'          <li><a class="les" href="index.html"{cur}><span class="n" aria-hidden="true">{ICON["flag"]}</span><span>Module overview</span></a></li>')
    for f,num,t,sub,mins,secs in ch['lessons']:
        cur = ' aria-current="page"' if f==current else ''
        ncls = 'n tip-n' if num in SPECIAL else 'n'
        li = f'          <li>\n            <a class="les" href="{f}"{cur}><span class="{ncls}">{num}</span><span>{t}</span></a>'
        if f==current and secs:
            li += '\n            <div class="sections" aria-label="Sections in this lesson">\n' + \
                  '\n'.join(f'              <a href="#{i}">{s}</a>' for i,s in secs) + '\n            </div>'
        items.append(li + '\n          </li>')
    return f'''
  <nav class="chapnav" aria-label="Module {n} lessons">
    <details id="chapdetails" open>
      <summary>
        <span>
          <span class="chap-label">Module {n}</span>
          <span class="chap-title">{ch['title']}</span>
        </span>
        <span class="summary-toggle" aria-hidden="true"><span class="when-closed">Lessons</span><span class="when-open">Close</span></span>
      </summary>
      <div class="panel">
        <ol>
{chr(10).join(items)}
        </ol>
        <a class="home-link" href="../../index.html#contents">{ICON['home']} All modules</a>
      </div>
    </details>
  </nav>
'''

def pagenav(ch, cur, wide=False):
    P = pages_of(ch); names = [p[0] for p in P]; i = names.index(cur)
    out = '    <div class="row{}"><div class="main">\n      <nav class="pagenav" aria-label="Page navigation">\n'.format(' wide' if wide else '')
    if i == 0:
        out += f'        <a href="../../index.html" aria-label="Book home" title="Book home">{ICON["home"]}<span><small>Back to</small>Book home</span></a>\n'
    else:
        pf, pt = P[i-1]
        out += f'        <a href="{pf}" aria-label="Previous: {pt}" title="Previous: {pt}">{ICON["prev"]}<span><small>Previous</small>{pt}</span></a>\n'
    if i < len(P)-1:
        nf, nt = P[i+1]
        out += f'        <a class="next" href="{nf}" aria-label="Next: {nt}" title="Next: {nt}"><span><small>Next</small>{nt}</span>{ICON["next"]}</a>\n'
    else:
        out += f'        <a class="next" href="../../index.html#contents" aria-label="End of Module {ch["n"]}: back to book contents" title="End of Module {ch["n"]}: back to book contents"><span><small>End of Module {ch["n"]}</small>Book contents</span>{ICON["home"]}</a>\n'
    return out + '      </nav>\n    </div></div>\n'

def crumbs(ch, label):
    return f'''    <nav class="crumbs" aria-label="Breadcrumb">
      <ol>
        <li><a href="../../index.html">Home</a></li>
        <li><a href="index.html">Module {ch['n']}</a></li>
        <li><span aria-current="page">{label}</span></li>
      </ol>
    </nav>
'''

def lesson_header(ch, idx):
    f,num,t,sub,mins,secs = ch['lessons'][idx]; total = len(ch['lessons'])
    kicker = num if num in SPECIAL else f'Lesson {num}'
    subp = f'\n        <p class="lesson-sub">{sub}</p>' if sub else ''
    m = f'<span>{ICON["clock"]} About {mins} minutes</span>' if mins else ''
    pct = round(100*(idx+1)/total)
    return f'''    <div class="row">
      <div class="main">
        <span class="lesson-kicker">{kicker}</span>
        <h1>{t}</h1>{subp}
        <div class="lesson-meta">
          {m}
          <span>{idx+1} of {total} in this module</span>
          <span class="progress" aria-hidden="true"><i style="width:{pct}%"></i></span>
        </div>
      </div>
    </div>
'''

STUB = '''    <!-- STUB: replace with converted lesson content -->
    <div class="row gap-md">
      <div class="main">
        <div class="note note-see">
          <div class="label">Coming soon</div>
          <p>This lesson is being moved into the guidebook. Until then, you'll find it in your course in Blackboard.</p>
        </div>
      </div>
    </div>
'''

def toolbar(ch, slim=False):
    items=[]
    for k in ch['es']:
        nm = ESSENTIAL[k]
        if slim:
            items.append(f'<li class="tb-skill" title="{nm.replace("&amp;","&")}">{coin_sm(k)}<span class="sr-only">{nm}</span></li>')
        else:
            items.append(f'<li class="tb-skill">{coin_sm(k)}<span class="tb-name">{nm}</span></li>')
    cls = 'skillbar slim' if slim else 'skillbar'
    lab = '10 Essential Skills in this module' if slim else "10 Essential Skills you'll build"
    return f'''<div class="{cls}" role="region" aria-label="{lab}">
  <div class="sb-inner">
    <span class="sb-label">{lab}</span>
    <ul class="sb-list">{''.join(items)}</ul>
  </div>
</div>'''

def coin_sm(k):
    return f'<span class="coin-sm"><img src="../../images/shared/10es/10es-{k:02d}.png" alt="" width="160" height="160"><span class="n">{k}</span></span>'

# ------------------------------------------------------------------ build chapter
def merit_note(ch):
    """Reminder on the overview of each module that a Merit activity is due with (Modules 4, 7, 10)."""
    m = ch.get('merit')
    if not m: return ''
    up = '' if ch['n'] == 2 else '../ch02/'
    return f'''
    <div class="row wide gap-sm">
      <div class="main">
        <div class="merit-note" role="note">
          <span class="merit-badge" aria-hidden="true">M</span>
          <div>
            <p class="merit-h">Merit reminder: Merit Activity #{m} is due with this module</p>
            <p>Submit it on the Merit platform. Check Blackboard for the due date and the activity options. Need to set up your page first? See <a href="{up}trail-tip-merit.html">Setting Up Your Merit Page</a>.</p>
          </div>
        </div>
      </div>
    </div>
'''

def build_chapter(ch):
    n = ch['n']; d = ROOT/f'chapters/ch{n:02d}'; d.mkdir(parents=True, exist_ok=True)
    where = f'Module {n} · {ch["title"]}'
    # lessons
    for i,(f,num,t,sub,mins,secs) in enumerate(ch['lessons']):
        label = num if num in SPECIAL else f'Lesson {num}'
        bp = HERE/f'bodies/ch{n:02d}/{f}'
        body = tokens(bp.read_text()) if bp.exists() else STUB
        title = (t if num in SPECIAL else f'{num} {t}')
        page = head(f'{re.sub("<[^>]+>","",title)} | Module {n} | {BOOK}', 2) + bookbar(2, where) + \
          '\n<div class="shell">\n' + sidebar(ch, f) + '\n  <main id="main" class="reading">\n' + toolbar(ch, slim=True) + crumbs(ch, label) + \
          lesson_header(ch, i) + '\n' + body + pagenav(ch, f) + '  </main>\n</div>\n' + FOOT
        write(d/f, page)

    # opener parts
    why = '\n'.join(f'          <p>{p}</p>' for p in ch['why'])
    letters = 'ABCDEFGH'; objs = []
    for k,(txt, inc) in enumerate(ch['objectives']):
        L = letters[k]
        if isinstance(inc, str) and inc.startswith('Mile Marker'):
            mark = f'''
            <a class="in-course" href="mile-marker.html">{ICON['pen']} You'll show this in {inc}</a>'''
        elif isinstance(inc, str):
            mark = f'''
            <span class="in-course">{ICON['pen']} You'll show this in {inc}</span>'''
        elif inc:
            mark = f'''
            <span class="in-course">{ICON['pen']} You'll practice this in your course activities</span>'''
        else:
            mark = ''
        objs.append(f'''          <li>
            <span class="obj-letter" aria-hidden="true">{L}</span>
            <div>
              <p class="obj-text"><span class="sr-only">Objective {L}: </span><strong>I can</strong> {txt}</p>{mark}
            </div>
          </li>''')
    es = []
    for k in ch['es']:
        if k in FOCUS:
            es.append(f'<li class="badge badge-10es badge-focus">{coin_sm(k)}<span class="btext"><span class="bname">{ESSENTIAL[k]}</span><span class="focus">Course focus skill</span></span></li>')
        else:
            es.append(f'<li class="badge badge-10es">{coin_sm(k)}<span class="btext"><span class="bname">{ESSENTIAL[k]}</span></span></li>')
    be = ''.join(f'<li class="badge badge-be">{BE_ICON[b]} BE {b}</li>' for b in ch['be'])
    be_note = f'\n            <p class="skill-note">{ch["be_note"]}</p>' if ch['be_note'] else ''
    cards = []
    for f,num,t,sub,mins,secs in ch['lessons']:
        cls = 'lesson-card tip' if num in SPECIAL else 'lesson-card'
        meta = [f'<span>{ICON["clock"]}About {mins} minutes</span>'] if mins else []
        if f in ch['builds']: meta.append(f'<span>Builds toward {ch["builds"][f]}</span>')
        cards.append(f'''          <li>
            <a class="{cls}" href="{f}">
              <span class="lesson-num">{num}</span>
              <div>
                <h3>{t}</h3>
                <p>{sub}</p>
                <span class="lesson-meta">{"".join(meta)}</span>
              </div>
            </a>
          </li>''')
    first = ch['lessons'][0][0]
    opener = head(f'Module {n}: {re.sub("<[^>]+>","",ch["title"])} | {BOOK}', 2) + bookbar(2, where) + f'''
<div class="banner">
  <div class="inner">
    <p class="chapter-kicker"><span class="chapter-num" aria-hidden="true">{n}</span>Module {n}</p>
    <h1>{ch['title']}</h1>
    <p class="tagline">{ch['tagline']}</p>
  </div>
  {banner_svg(str(n))}
</div>
{toolbar(ch)}

<div class="shell">
''' + sidebar(ch, 'index.html') + f'''
  <main id="main" class="reading opener">

    <section aria-labelledby="why" class="row wide gap-sm">
      <div class="main">
        <div class="sticky">
          <h2 id="why">Why this matters</h2>
{why}
        </div>
      </div>
    </section>
{merit_note(ch)}
    <span class="rest wide" aria-hidden="true"></span>

    <!-- LEARNING OBJECTIVES: Competency Framework I Can {n}.x, verbatim. -->
    <section aria-labelledby="objectives" class="row wide">
      <div class="main">
        <div class="h2wrap"><h2 id="objectives">What you'll be able to do</h2></div>
        <p class="obj-intro">By the end of this module:</p>
        <ol class="objectives">
{chr(10).join(objs)}
        </ol>
      </div>
      <div class="main be-block">
        <h3 class="be-h">AI Literacy: BE behaviors in this module</h3>
        <ul class="badges">{be}</ul>{be_note}
      </div>
    </section>

    <span class="rest wide" aria-hidden="true"></span>

    <section aria-labelledby="lessons" class="row wide">
      <div class="main">
        <div class="h2wrap"><h2 id="lessons">Lessons in this module</h2></div>
        <ol class="lessons">
{chr(10).join(cards)}
        </ol>
        <div class="start-row">
          <a class="start-btn" href="{first}">Start Module {n} {TOK['next']}</a>
        </div>
      </div>
    </section>

''' + pagenav(ch, 'index.html', wide=True) + '  </main>\n</div>\n' + FOOT
    write(d/'index.html', opener)

# ------------------------------------------------------------------ home
def build_home():
    toc = []
    for ch in CHAPTERS:
        n = ch['n']
        les = '\n'.join(
          f'              <li><a href="chapters/ch{n:02d}/{f}"><span class="{"n tip-n" if num in SPECIAL else "n"}">{num}</span><span>{tt}</span></a></li>'
          for f,num,tt,*_ in ch['lessons'])
        toc.append(f'''        <li>
          <span class="cnum" aria-hidden="true">{n}</span>
          <div>
            <h3><a href="chapters/ch{n:02d}/index.html"><span class="sr-only">Module {n}: </span>{ch['title']}</a></h3>
            <details class="toc-more">
              <summary>What's inside <span class="sr-only">Module {n}</span></summary>
              <p class="cdesc">{ch['desc']}</p>
              <ol class="toc-lessons" aria-label="Module {n} lessons">
{les}
              </ol>
            </details>
          </div>
        </li>''')
    for n,t,dsc in LATER:
        toc.append(f'''        <li class="pending">
          <span class="cnum" aria-hidden="true">{n}</span>
          <div>
            <h3><span class="sr-only">Module {n}: </span>{t} <span class="soon">Coming soon</span></h3>
            <details class="toc-more">
              <summary>What's inside <span class="sr-only">Module {n}</span></summary>
              <p class="cdesc">{dsc}</p>
            </details>
          </div>
        </li>''')
    home = head(f'{BOOK} | FYE 100: Strategies for College Success', 0) + bookbar(0, '') + f'''
<div class="hero">
  <div class="inner">
    <p class="eyebrow">FYE 100 · Strategies for College Success</p>
    <h1>{BOOK}</h1>
    <p class="tagline">Your guide to college, from your first week to the skills you'll carry with you.</p>
    <a class="start-btn" href="chapters/ch01/index.html">Start reading {TOK['next']}</a>
  </div>
  {banner_svg('START HERE')}
</div>

<main id="main" class="home">
  <p class="home-intro">This guidebook holds the readings for FYE 100. Your course in Blackboard tells you what's due and when. This is where you read, think, and get ready.</p>

  <section aria-labelledby="contents" class="gap-md">
    <div class="h2wrap"><h2 id="contents">Contents</h2></div>
    <ol class="toc">
{chr(10).join(toc)}
    </ol>
  </section>
</main>
''' + FOOT
    write(ROOT/'index.html', home)

for ch in CHAPTERS: build_chapter(ch)
build_home()
print('built', [c['n'] for c in CHAPTERS])
