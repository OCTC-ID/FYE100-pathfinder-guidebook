"""Pathfinder Guidebook generator: builds home page, chapter openers, and lesson pages
from chapter config + lesson body fragments in bodies/chNN/."""
import re, pathlib
HERE = pathlib.Path(__file__).parent
ROOT = HERE.resolve().parent   # the site root (this folder's parent)
V = 48
BOOK = 'Pathfinder Guidebook'

def svg(path, sw='2', extra='', cls='ic'):
    c = f'class="{cls}" ' if cls else ''
    return f'<svg {c}viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{path}</svg>'

ICON = {
 'flag': svg('<path d="M4 21V4M4 4h12l-2 4 2 4H4"/>'),
 'home': svg('<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/>'),
 'menu': svg('<path d="M4 6h16M4 12h16M4 18h10"/>', '2.2'),
 'help': svg('<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7M12 17h.01"/>'),
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
       "This module puts those things on the table early, while there's still time to build the right habits. What you set up here, including your goal, your sense of what college expects, and your first look at the skills and tools you'll use all semester, becomes the foundation for everything that follows. New to this book? Take a few minutes with <a href=\"../help/index.html\">How to Use This Book</a> first."],
  objectives=[("describe my personal reasons for attending college and define what success means to me right now.", 'Mile Marker #1'),
              ("navigate Blackboard and locate key course information, assignments, and instructor contact details.", 'the Syllabus &amp; Blackboard Scavenger Hunt (optional practice)'),
              ("set one personal or academic goal for this semester and describe how I plan to reach it.", 'Mile Marker #1'),
              ("explain what artificial intelligence is and identify where it already shows up in my daily life.", 'Mile Marker #1')],
  es=[1,5,6,10], be=['Safe','Honest'], be_note='This module also introduces all five BE behaviors you\'ll use throughout the book.',
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
  builds={'1-3.html':'D','1-4.html':'D','1-5.html':'B','trail-tip.html':'B','mile-marker.html':'A, C, D'}),

 dict(n=2, title='Building Your Support System',
  desc='Map the people and resources around you, meet your Success Coach, and practice asking for help.',
  tagline='No one completes a journey alone. Every great Pathfinder relies on maps, tools, and traveling companions.',
  why=["College success isn't just about willpower. It's about knowing when and where to reach out. The students who struggle most aren't always the ones who don't know things. They're the ones who wait too long to ask.",
       "This module helps you build your support map: the people and resources you can actually use when things get hard. That network is one of the smartest investments you can make right now."],
  objectives=[("identify people and OCTC resources that can support my success and explain how each one helps.", 'Mile Marker #2'),
              ("describe how I will use my support system intentionally this semester.", 'Mile Marker #2'),
              ("identify one new campus resource I want to explore and explain why it matters for my goals.", 'Mile Marker #2'),
              ("practice asking for help clearly and specifically in a realistic college scenario.", 'the AI Chat: Who Has Your Back?')],
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
 dict(n=5, title='Financial Planning with Purpose',
  desc="Build a zero-based budget, look honestly at your spending patterns, and explore what financial wellness means for your overall wellbeing.",
  tagline="Money touches everything. This module is about seeing it clearly, before trying to change anything.",
  why=["Financial stress is one of the biggest, and least talked about, barriers to college success. It isn't just uncomfortable. It's mentally expensive: your brain keeps working on money problems in the background, even when you're trying to focus on something else.",
       "This module won't tell you to follow a strict budget or stop buying coffee. It will help you see your financial situation more clearly, and give your money a plan that fits your real life. That's the only honest starting point."],
  objectives=[("build a realistic zero-based budget that assigns all available income to specific categories.", 'Mile Marker #5'),
              ("identify at least one pattern in my spending habits and describe one small change I want to make.", 'Mile Marker #5'),
              ("explain what financial wellness means and describe how it connects to my overall wellbeing.", 'Mile Marker #5'),
              ("use AI tools safely for budgeting exploration without sharing personal financial information.", 'Mile Marker #5')],
  es=[3,6], be=['Safe','Responsible'], be_note='',
  lessons=[
   ('dollar-tracker.html','Trail Tool','Dollar Tracker',"Look back: where your money actually goes.",5,
     [('form','Fill in your tracker')]),
   ('budget-builder.html','Trail Tool','Budget Builder',"Look ahead: give every dollar a job.",10,
     [('form','Build your budget')]),
   ('5-1.html','5.1','Skill Spotlight: Quantitative Reasoning',"Thinking clearly with numbers, which you already do every day.",6,
     [('name-it','Name the thing'),('already','You already do this'),('headed',"Where you're headed"),('module','Where it shows up'),('anxiety','Math anxiety'),('life','In your own life')]),
   ('5-2.html','5.2','What Is Financial Wellness?',"A feeling of steadiness you can work toward from wherever you're starting.",7,
     [('is',"What it is, and isn't"),('dimensions','Eight dimensions'),('stress','Money stress and school')]),
   ('5-3.html','5.3','Where Does My Money Go?',"You can't manage what you can't see. Awareness comes first.",10,
     [('steps','Three steps'),('every-dollar','Give every dollar a job'),('tools','Tools'),('ai-money','AI and money')]),
   ('mile-marker.html','Mile Marker','Mile Marker #5: Understanding My Money',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 5 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'dollar-tracker.html':'B','budget-builder.html':'A','5-2.html':'C','5-3.html':'A, B, D','mile-marker.html':'A, B, C, D'}),
 dict(n=6, title='Map Your Path — Academic Planning',
  desc="Explore your interests, learn the difference between certificates, diplomas, and degrees, and prepare the questions you'll bring to your Success Coach.",
  tagline="Your plan doesn't have to be final. It has to be specific enough to start a real conversation.",
  why=["Most students walk into advising appointments without a plan, and walk out with a generic schedule that may or may not fit their actual goals.",
       "This module helps you explore programs that might fit, understand how credentials stack at OCTC, and build the specific questions that turn a routine appointment into a useful one."],
  objectives=[("interpret my Career Coach or O*NET Interest Profiler results and connect them to at least one program or career direction at OCTC.", 'Mile Marker #6'),
              ("describe the difference between certificates, diplomas, AAS degrees, and transfer pathways at OCTC.", 'Mile Marker #6'),
              ("draft a realistic course load for next semester based on my goals, schedule, and program requirements.", 'Mile Marker #6'),
              ("write five specific questions to bring to my Success Coach advising appointment.", 'Mile Marker #6'),
              ("use AI responsibly to explore academic pathways without sharing personal identifying information.", True)],
  es=[1,6,9,10], be=['Responsible','Reflective'], be_note='',
  lessons=[
   ('academic-planner.html','Trail Tool','Academic Planner',"Look ahead: sketch your next semesters and the questions to bring.",15,
     [('form','Fill in your plan')]),
   ('6-1.html','6.1','Skill Spotlight: Knowledge Application',"Turning what you know into real decisions.",5,
     [('what','What this skill is'),('headed',"Where you're headed"),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('6-2.html','6.2','Explore Your Interests with Career Coach',"Take the assessment, read your results, and see what they point toward.",8,
     [('riasec','Six interest types'),('take','Take the assessment'),('results','Use your results'),('ai-results','AI and your results')]),
   ('6-3.html','6.3','Programs &amp; Pathways at OCTC',"How credentials stack, and how your results connect to real programs.",8,
     [('stack','How credentials stack'),('types','What each one means'),('connect','Connect your results'),('bring','What to bring')]),
   ('6-4.html','6.4','Build a Simple Academic Plan',"A map, not a rigid schedule.",9,
     [('strategist','Think like a strategist'),('examples','What it looks like'),('questions','Questions to bring'),('ai-plan','AI and your plan')]),
   ('trail-tip-grades.html','Trail Tip','Wait... How Is My Grade Actually Calculated?',"Most students don't know. Now you will.",8,
     [('in-class','In a class'),('gpa','Your GPA'),('practice','Try it')]),
   ('mile-marker.html','Mile Marker','Mile Marker #6: My Academic Plan',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 6 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'academic-planner.html':'C, D','6-2.html':'A, E','6-3.html':'A, B','6-4.html':'C, D, E','mile-marker.html':'A, B, C, D'}),
 dict(n=7, title='Knowing Your Strengths &amp; Values',
  desc="Discover your top strengths and personal values, and connect them to your academic habits and career direction.",
  tagline="Not what you're doing. Who you are, and what you bring to everything you do.",
  why=["You've spent the last several modules building awareness of your time, your money, and your academic direction. This module turns the focus inward: not what you're doing, but who you are.",
       "Your strengths and values shape how you learn, how you work with others, what drains you, and what energizes you. Understanding them is one of the most useful things you can do for the rest of this semester, and beyond."],
  objectives=[("identify my Top 5 HIGH5 strengths and explain what they mean for how I learn and work.", 'Mile Marker #7'),
              ("identify my Top 5 personal values and describe how they shape my decisions and priorities.", 'the Values Journal (online) or class discussion (in person)'),
              ("connect my strengths and values to my academic habits, career direction, and how I work with others.", 'Mile Marker #7'),
              ("recognize one blind spot that comes with my strengths and describe what to watch for.", 'Mile Marker #7')],
  es=[5,9], be=['Reflective'], be_note='', merit=2,
  lessons=[
   ('my-values-snapshot.html','Trail Tool','My Values Snapshot',"Your Top 5 values, why they matter, and where they show up.",10,
     [('form','Fill in your snapshot')]),
   ('7-1.html','7.1','Skill Spotlight: Adaptability &amp; Leadership',"Not a title. How you show up, especially when things change.",5,
     [('what','What this skill is'),('headed',"Where you're headed"),('looks-like','What it looks like'),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('7-2.html','7.2','Why Your Personal Values Matter',"Interests tell you what you enjoy. Values tell you who you are.",8,
     [('shape','What values shape'),('vs','Interests and values'),('shifting','If interests keep shifting'),('sort','The Values Card Sort'),('use','Use your results')]),
   ('7-3.html','7.3','What Are Strengths, and Why Do They Matter?',"Not just what you're good at. What feels like you at your best.",9,
     [('real-life','In real life'),('baseline','A quick baseline'),('take','Take HIGH5'),('mean','What results mean'),('blind','Blind spots'),('ai-strengths','AI and your results')]),
   ('mile-marker.html','Mile Marker','Mile Marker #7: My Strengths Snapshot',"The assignment, with support, and a form you can fill in and save.",10,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 7 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'my-values-snapshot.html':'B','7-1.html':'C','7-2.html':'B, C','7-3.html':'A, C, D','mile-marker.html':'A, C, D'}),
 dict(n=8, title='Explore Your Career Options',
  desc="Research one career in depth, then honestly evaluate whether it fits your strengths, values, work style, and life.",
  tagline="Not the career you're supposed to want. The one that actually fits who you are.",
  why=["A good career fit isn't just about choosing something that \"sounds cool\" or \"pays well.\" It's about finding work that lines up with who you are, what you value, what you're good at, and how you actually want to live.",
       "In this module you'll use real research tools to explore one career in depth, and honestly assess whether it fits. You'll also set up your Handshake profile and get ready to register for next semester."],
  objectives=[("research one career using Career Coach and O*NET, including regional salary, job outlook, education requirements, and typical work environment.", 'Mile Marker #8'),
              ("evaluate a career for personal fit by connecting my research findings to my strengths, values, work style, and pressure tolerance.", 'Mile Marker #8'),
              ("articulate one clear question I still have about this career direction.", 'Mile Marker #8')],
  es=[1,2,6,10], be=['Critical','Responsible'], be_note='',
  lessons=[
   ('career-research-guide.html','Trail Tool','Career Research Guide',"One career, researched well, and an honest look at the fit.",30,
     [('form','Fill in your research')]),
   ('8-1.html','8.1','Skill Spotlight: Communication',"Showing up in the conversation as someone worth listening to.",7,
     [('what','What this skill is'),('headed',"Where you're headed"),('behaviors','Three behaviors'),('module','Where it shows up'),('email','A Milestone email'),('life','In your own life'),('later','How it shows up later')]),
   ('8-2.html','8.2','Research Your Career',"What fits, what doesn't, and how to find out.",10,
     [('fit','What career fit means'),('directions','Directions, not titles'),('before','Start with the life you want'),('tools','Two research tools'),('how','Step by step'),('ai-research','AI and career research')]),
   ('trail-tip-handshake.html','Trail Tip','Set Up Your Handshake Profile',"Your professional home base, starting now.",5,
     [('setup','Set up your profile'),('explore','Worth exploring')]),
   ('trail-tip-register.html','Trail Tip','Register Early for Next Semester',"Early gets the classes you need. Late gets what's left.",4,
     [('when','When registration opens'),('coach','Meet your Success Coach'),('why','Why early matters')]),
   ('mile-marker.html','Mile Marker','Mile Marker #8: My Career Snapshot',"The assignment, with support, and a form you can fill in and save.",10,
     [('part1','Part 1: Research Guide'),('questions','Part 2: The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 8 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'career-research-guide.html':'A, B, C','8-2.html':'A, B','mile-marker.html':'A, B, C'}),
 dict(n=9, title='Think It Through — Critical Thinking + STAR(T) Introduction',
  desc="Build your critical thinking toolkit with the 4C Check, and meet the STAR(T) framework for telling your story.",
  tagline="The 4C Check, your thinking patterns, and your first STAR(T) draft.",
  why=["This module is about thinking on purpose: noticing the assumptions and thought traps that get in your way, and using a simple tool, the 4C Check, to think more clearly.",
       "The second half connects straight to your capstone. You'll write your first STAR(T) draft and use the same 4C Check to make it clearer, more honest, and more specific."],
  objectives=[("identify one thinking habit that sometimes gets in my way and name a strategy for interrupting it.", 'Mile Marker #9'),
              ("apply the 4C Check (Clarity, Context, Credibility, Consequences) to evaluate a real situation or decision.", 'the AI Chat: Think It Through'),
              ("explain the STAR(T) framework and describe how each of the five steps works.", 'Mile Marker #9'),
              ("draft one practice STAR(T) response using a real experience and apply the 4C Check to strengthen it.", 'Mile Marker #9')],
  es=[1,2,9], be=['Critical','Reflective'], be_note='',
  lessons=[
   ('four-c-check.html','Trail Tool','4C Check',"Walk through any decision, one C at a time.",10,
     [('form','Work through your decision')]),
   ('9-1.html','9.1','Skill Spotlight: Critical &amp; Creative Thinking',"Pausing on purpose before you react, decide, or assume.",6,
     [('what','What this skill is'),('headed',"Where you're headed"),('behaviors','Three behaviors'),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('9-2.html','9.2','What Is Critical Thinking, Really?',"It's not overthinking. It's thinking with intention.",5,
     [('is',"What it is, and isn't"),('habits','Four habits'),('examples','In real life')]),
   ('9-3.html','9.3','Spotting Assumptions, Biases &amp; Thought Traps',"Everyone falls into these patterns. The trick is noticing them.",8,
     [('assumptions','Assumptions'),('biases','Biases'),('traps','Thought traps'),('why','Why it matters'),('practice','Spot the trap')]),
   ('9-4.html','9.4','The 4C Check: A Simple Tool for Better Decisions',"Pause, get clear, and choose wisely.",8,
     [('four','The four Cs'),('example','Putting it together'),('try','Try it'),('practice','Practice with Coach Pathfinder')]),
   ('9-5.html','9.5','Think It Through: Using Critical Thinking to Build Your STAR(T) Story',"The thinking behind a good decision also makes a story worth telling.",9,
     [('refresher','STAR(T) in five steps'),('traps','Traps in STAR(T) drafts'),('check','The 4C Check on a draft'),('interview','Your interview answer')]),
   ('mile-marker.html','Mile Marker','Mile Marker #9: Think It Through',"The assignment, with support, and a form you can fill in and save.",15,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 9 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'four-c-check.html':'B','9-3.html':'A','9-4.html':'B','9-5.html':'C, D','mile-marker.html':'A, C, D'}),
 dict(n=10, title='Team Up — Collaboration &amp; People Skills', merit=3,
  desc="Explore how you work with others, name your collaboration strengths and challenges, and figure out what you need from a team.",
  tagline="How you work with others, and how to make it easier on everyone, including you.",
  why=["Let's be honest: group work has a reputation, and not always a great one. This module isn't about pretending it's easy. It's about figuring out how <em>you</em> work best, so you can say so, instead of just hoping things go okay.",
       "You'll take the 16Personalities assessment, look at your collaboration strengths and struggles, and pick up strategies that fit how you operate. All of it feeds straight into Mile Marker #10."],
  objectives=[("identify my natural collaboration tendencies using my 16Personalities results and explain how they show up in group work.", 'Mile Marker #10'),
              ("name two collaboration strengths and one or two challenges and explain why those challenges happen.", 'Mile Marker #10'),
              ("describe three specific strategies that help me work more effectively with others.", 'Mile Marker #10'),
              ("articulate in one clear sentence what I need from teammates to do my best work.", 'Mile Marker #10')],
  es=[1,4,8], be=['Honest','Responsible'], be_note='',
  lessons=[
   ('collaboration-snapshot.html','Trail Tool','Collaboration Snapshot',"Your roles, type, strengths, struggles, and strategies in one place.",15,
     [('form','Fill in your snapshot')]),
   ('10-1.html','10.1','Skill Spotlight: Collaboration &amp; Teamwork',"Yes, the group work skill. Stay with us. This one's worth it.",7,
     [('what','What this skill is'),('headed',"Where you're headed"),('behaviors','Four behaviors'),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('10-2.html','10.2','Who Are You in a Group?',"Before you can work well with others, you have to understand how you naturally show up.",5,
     [('roles','Seven group roles'),('messy','Where it gets messy'),('tools','Why personality tools help'),('reflect','Start your snapshot')]),
   ('10-3.html','10.3','Exploring Your Personality Type',"Take the 16Personalities assessment and make sense of your results.",15,
     [('take','Take the assessment'),('letters','Understand your letters'),('groups','Your type in groups'),('map','A map, not a rulebook'),('impressions','First impressions')]),
   ('10-4.html','10.4','Strengths &amp; Struggles in Collaboration',"Every style has strengths and challenges. Knowing yours is power.",6,
     [('traits','Your type and collaboration'),('brains','Different brains'),('yours','Name your strengths')]),
   ('10-5.html','10.5','Collaborative Strategies That Actually Work',"Choose strategies that match how you work.",8,
     [('strategies','Nine strategies'),('choose','Choose your three')]),
   ('trail-tip-ai-plan.html','Trail Tip','Divide &amp; Conquer, AI-Style',"Use AI to turn a group assignment into tasks, roles, and a timeline.",5,
     [('how','How to do it'),('example','What you get back'),('ai','The plan is the easy part')]),
   ('mile-marker.html','Mile Marker','Mile Marker #10: My Collaboration Profile',"The assignment, with support, and a form you can fill in and save.",15,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 10 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'collaboration-snapshot.html':'A, B, C, D','10-2.html':'A','10-3.html':'A','10-4.html':'B','10-5.html':'C, D','trail-tip-ai-plan.html':'C','mile-marker.html':'A, B, C, D'}),
 dict(n=11, title='Making an Impact — Community, Values &amp; Your Pathfinder Journey',
  desc="See how communities work, connect your strengths and values to how you want to show up in them, and choose your four STAR(T) Stories.",
  tagline="Your community is closer than you think, and so is your next step on this trail.",
  why=["\"Civic engagement\" can sound like something for other people: politicians, organizers, people with way more free time than you. This module starts somewhere different, with the communities you're already part of and the everyday skill of seeing how they actually work.",
       "It's also your working time for your STAR(T) Stories. Everything you've learned about yourself this semester (strengths, values, interests, and now community) is exactly what those stories are made of."],
  objectives=[("define community broadly and identify at least one community I already belong to and contribute to.", 'Mile Marker #11'),
              ("describe specific ways my everyday actions make a positive impact on the people around me.", 'Mile Marker #11'),
              ("connect my strengths and values to one intentional way I want to grow my community impact going forward.", 'Mile Marker #11'),
              ("select four experiences from my semester and match each one to an Essential Skill for my STAR(T) Story.", 'Mile Marker #11')],
  es=[4,5,7,9], be=['Responsible','Reflective'], be_note='',
  lessons=[
   ('community-snapshot.html','Trail Tool','Community Snapshot',"One community: how it works, what you bring, and where you're headed.",15,
     [('form','Fill in your snapshot')]),
   ('11-1.html','11.1','Skill Spotlight: Civic Engagement',"Starting with the parts of \"society\" you're already standing in.",7,
     [('what','What this skill is'),('headed',"Where you're headed"),('behaviors','Three behaviors'),('module','Where it shows up'),('life','In your own life'),('later','How it shows up later')]),
   ('11-2.html','11.2','What Is Community, Really?',"You're already in more communities than you think, and already shaping how they work.",9,
     [('already',"You're already in community"),('system','Every community runs on a system'),('example','The shared kitchen'),('civic','Why this counts'),('try','Your turn'),('more','Systems thinking')]),
   ('11-3.html','11.3','Your Strengths, Your Community',"Putting what you know about yourself to work.",8,
     [('know',"What you've figured out"),('time','"I don\'t have time"'),('offer','Your offer and your boundary'),('example','Jordan and the garden'),('try','Your turn'),('next','Your stories are here')]),
   ('trail-tip-start.html','Trail Tip','Start Your STAR(T) Stories',"This module is your working time. Here's the short path.",3,
     [('path','Three steps to start')]),
   ('mile-marker.html','Mile Marker','Mile Marker #11: My Community Impact',"The assignment, with support, and a form you can fill in and save.",20,
     [('questions','The questions'),('ai-partner','AI thinking partner'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 11 Wrap Up',"Pull it together before you head back to your course.",2,
     [('takeaways','Key takeaways')]),
  ],
  builds={'community-snapshot.html':'A, B, C','11-2.html':'A, B','11-3.html':'C','trail-tip-start.html':'D','mile-marker.html':'A, B, C, D'}),
 dict(n=12, title='Reflecting Back, Moving Forward',
  desc="Look back at how far you've come, finish and submit your STAR(T) Stories, and decide what you're taking with you.",
  tagline="The last mile marker on the trail, and a look at everything you've built along the way.",
  why=["This is the last module of new content. From here, it's about finishing strong: completing your STAR(T) Stories, taking stock of how far you've come, and getting ready for the rest of the semester.",
       "Your STAR(T) Stories are your capstone: four true stories that show what you've built, in your own voice. Mile Marker #12 is short on purpose, so you can spend most of your time on them."],
  objectives=[("record four STAR(T) responses, one per selected Essential Skill, that are specific, honest, and clearly structured.", 'your STAR(T) Stories (capstone)'),
              ("articulate how each skill connects to my future in college, my career, and my life: the Transfer step.", 'your STAR(T) Stories (capstone)'),
              ("explain my choice of student-selected skill in my own words.", 'your STAR(T) Stories (capstone)'),
              ("reflect honestly on my growth this semester, what I am taking with me, and what I want to work on next.", 'Mile Marker #12')],
  es=[1,5,6,9], be=['Honest','Reflective'], be_note='Your STAR(T) Stories bring all ten skills together: three assigned, and one you choose.',
  lessons=[
   ('look-back.html','Trail Tool','Look Back',"Your Mile Markers in one place, and room to notice what stands out.",15,
     [('trail','Your Mile Markers'),('form','Fill in your look back')]),
   ('12-1.html','12.1','Finish Your STAR(T) Stories',"Final review, and how to submit your capstone.",8,
     [('where','Where you are'),('review','Final review'),('submit','Submitting your stories')]),
   ('trail-tip-finish.html','Trail Tip','Finishing Strong',"FYE 100 may end before your other classes do. Here's how to finish the semester.",3,
     [('finals','Heading into finals')]),
   ('mile-marker.html','Mile Marker','Mile Marker #12: My Story to Share',"Your final reflection, with support, and a form you can fill in and save.",20,
     [('before','A quick look back'),('questions','The questions'),('scoring',"How it's scored"),('form','Fill in and save')]),
   ('wrap-up.html','Wrap Up','Module 12 Wrap Up',"You've walked the whole trail.",2,
     [('takeaways',"What you're taking with you")]),
  ],
  builds={'look-back.html':'D','12-1.html':'A, B, C','mile-marker.html':'D'}),
]
LATER = [
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
    <nav class="bar-nav" aria-label="Book">
      <a class="bar-btn" href="{up}index.html">{ICON['home']}<span class="bar-lbl">Home</span></a>
      <a class="bar-btn" href="{up}chapters/help/index.html">{ICON['help']}<span class="bar-lbl">How to use</span></a>
      <a class="contents-btn" href="{up}index.html#contents">{ICON['menu']}<span><span class="long">Book </span>Contents</span></a>
    </nav>
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
    return [('index.html',ch.get('overview','Module overview'))] + [(l[0], l[2] if l[1] in SPECIAL else f'{l[1]} {l[2]}') for l in ch['lessons']]

def sidebar(ch, current):
    n = ch['n']; items = []; lab = ch.get('label', f'Module {n}')
    cur = ' aria-current="page"' if current=='index.html' else ''
    items.append(f'          <li><a class="les" href="index.html"{cur}><span class="n" aria-hidden="true">{ICON["flag"]}</span><span>{ch.get("overview","Module overview")}</span></a></li>')
    for f,num,t,sub,mins,secs in ch['lessons']:
        cur = ' aria-current="page"' if f==current else ''
        ncls = 'n tip-n' if num in SPECIAL else 'n'
        li = f'          <li>\n            <a class="les" href="{f}"{cur}><span class="{ncls}">{num}</span><span>{t}</span></a>'
        if f==current and secs:
            li += '\n            <div class="sections" aria-label="Sections in this lesson">\n' + \
                  '\n'.join(f'              <a href="#{i}">{s}</a>' for i,s in secs) + '\n            </div>'
        items.append(li + '\n          </li>')
    return f'''
  <nav class="chapnav" aria-label="{lab} pages">
    <details id="chapdetails" open>
      <summary>
        <span>
          <span class="chap-label">{ch.get('navlabel', lab)}</span>
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
    P = pages_of(ch); names = [p[0] for p in P]; i = names.index(cur); lab = ch.get('label', f'Module {ch["n"]}')
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
        out += f'        <a class="next" href="../../index.html#contents" aria-label="End of {lab}: back to book contents" title="End of {lab}: back to book contents"><span><small>End of {lab}</small>Book contents</span>{ICON["home"]}</a>\n'
    return out + '      </nav>\n    </div></div>\n'

def crumbs(ch, label):
    return f'''    <nav class="crumbs" aria-label="Breadcrumb">
      <ol>
        <li><a href="../../index.html">Home</a></li>
        <li><a href="index.html">{ch.get('label', 'Module ' + str(ch['n']))}</a></li>
        <li><span aria-current="page">{label}</span></li>
      </ol>
    </nav>
'''

def lesson_header(ch, idx):
    f,num,t,sub,mins,secs = ch['lessons'][idx]; total = len(ch['lessons'])
    kicker = num if num in SPECIAL else f"{ch.get('kicker','Lesson')} {num}"
    subp = f'\n        <p class="lesson-sub">{sub}</p>' if sub else ''
    m = f'<span>{ICON["clock"]} About {mins} minutes</span>' if mins else ''
    pct = round(100*(idx+1)/total)
    return f'''    <div class="row">
      <div class="main">
        <span class="lesson-kicker">{kicker}</span>
        <h1>{t}</h1>{subp}
        <div class="lesson-meta">
          {m}
          <span>{idx+1} of {total} in this {ch.get('unit','module')}</span>
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

    return f'''
    <div class="row wide gap-sm">
      <div class="main">
        <div class="merit-note" role="note">
          <img class="merit-badge" src="../../images/shared/merit-badge.png" alt="" width="44" height="44">
          <div>
            <p class="merit-h">Merit reminder: Merit Activity #{m} is due with this module</p>
            <p>Find an activity, then submit your reflection to the Merit Activity #{m} link in Blackboard. Check Blackboard for the due date. The <a href="../merit/index.html">Merit Guide</a> has your options, what proof to include, and how to write your reflection.</p>
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

# ------------------------------------------------------------------ guides (appendix)
from merit_options import OPTIONS as MERIT_OPTIONS

GUIDES = [
 dict(n='M', slug='merit', label='Merit Guide', navlabel='Guide', unit='guide', overview='Guide overview', kicker='Part',
  title='Merit Guide', icon='images/shared/merit-badge.png',
  desc="Everything you need for your three Merit activities: setting up your page, finding an activity, what proof to include, and writing your reflection.",
  tagline="Learning that happens outside class counts. Here's how to find it, and how to make it count for you.",
  intro=["Merit activities run through the whole course, from setting up your Merit page early on to your third activity near the end. This guide keeps everything about them in one place, so you can come back to it whenever you need it.",
         "Whether you take classes on campus or online, you'll find a path that works for you."],
  lessons=[
   ('how-it-works.html','1','How Merit Works in FYE 100',"Three activities, paced across the course.",4,
     [('three','Three activities'),('steps','Start to finish'),('counts','What counts'),('why','Why it matters')]),
   ('setup.html','2','Setting Up Your Merit Page',"Your Merit page is your official record of involvement and achievement at OCTC.",5,
     [('why-merit','What Merit does for you'),('setup','Set up your page'),('links','Helpful links')]),
   ('find-activity.html','3','Find Your Activity',"On campus, online, or in your community.",5,
     [('paths','Three paths'),('approval','Getting approval'),('proof','Proof at a glance')]),
   ('on-demand.html','4','On-Demand Options',"Approved options you can do from anywhere. Updated each semester.",3,
     [('now',"What's available"),('how','Making it count')]),
   ('reflection.html','5','Write Your Reflection',"Going is the requirement. The reflection is where the learning happens.",5,
     [('format','Choose a format'),('prompts','Three prompts'),('example','An example'),('scoring',"How it's scored"),('submit','Before you submit')]),
   ('merit-reflection.html','Trail Tool','Merit Reflection',"Draft it, count your words, and copy it into Blackboard.",10,
     [('form','Draft your reflection')]),
  ],
  source={'setup.html':'ch02/trail-tip-merit.html'}),
 dict(n='S', slug='start', label='STAR(T) Stories Guide', navlabel='Guide', unit='guide', overview='Guide overview', kicker='Part',
  title='STAR(T) Stories Guide', icon='images/shared/start-badge.svg',
  desc="Your capstone: four true stories that show four Essential Skills. The framework, how to find your stories, how to record them, and a practice guide for each.",
  tagline="Anyone can claim a skill. Your stories show it.",
  intro=["Your capstone for FYE 100 is four STAR(T) Stories: short, true stories about times you showed four of the 10 Essential Skills. Each one follows the same five steps: Situation, Task, Action, Result, and Transfer.",
         "You can record your stories or type them. Recording is strongly encouraged, because \"Tell me about a time when...\" is exactly what you'll hear in job interviews, and telling your story out loud now is the best practice you can get. Recordings are never scored on delivery, only on the story and its structure."],
  extra='''    <section aria-labelledby="four-h" class="row wide">
      <div class="main">
        <div class="h2wrap"><h2 id="four-h">Your four stories</h2></div>
        <ul class="four-stories">
          <li><a href="practice-adaptability.html"><span class="coin coin-md"><img src="../../images/shared/10es/10es-05.png" alt="" width="160" height="160"><span class="sn">5</span></span><span class="fs-name">Adaptability &amp; Leadership</span></a></li>
          <li><a href="practice-professionalism.html"><span class="coin coin-md"><img src="../../images/shared/10es/10es-06.png" alt="" width="160" height="160"><span class="sn">6</span></span><span class="fs-name">Professionalism</span></a></li>
          <li><a href="practice-knowledge.html"><span class="coin coin-md"><img src="../../images/shared/10es/10es-09.png" alt="" width="160" height="160"><span class="sn">9</span></span><span class="fs-name">Knowledge Application</span></a></li>
          <li><a href="practice-choice.html"><span class="coin coin-md coin-choice"><span class="choice-mark" aria-hidden="true">?</span></span><span class="fs-name">Your choice</span></a></li>
        </ul>
      </div>
    </section>

    <span class="rest wide" aria-hidden="true"></span>
''',
  lessons=[
   ('the-framework.html','1','The STAR(T) Framework',"Five steps for telling the story of a skill you've actually built.",6,
     [('steps','The five steps'),('example','What it looks like')]),
   ('find-your-stories.html','2','Find Your Stories',"Four skills, four true stories. Here's how to pick them.",10,
     [('four','Your four skills'),('prompts','Prompts for every skill'),('mine','Mine your own work'),('good','Is it a good story?')]),
   ('tell-it-out-loud.html','3','Tell It Out Loud',"Why recording is worth it, and how to do it in 2 to 4 minutes.",6,
     [('not-speech','Not a speech class'),('ramble','The rambling problem'),('options','Your options'),('record','Recording in Blackboard')]),
   ('strong-story.html','4','What Makes a Strong Story',"How stories are scored, and three fixes that move a story up.",5,
     [('levels','How stories are scored'),('upgrade','Three fixes'),('submit','Submitting')]),
   ('practice-adaptability.html','Trail Tool','Practice Guide: Adaptability &amp; Leadership',"Find your story and draft it, one step at a time.",20,
     [('find','Find your story'),('form','Draft it')]),
   ('practice-professionalism.html','Trail Tool','Practice Guide: Professionalism',"Find your story and draft it, one step at a time.",20,
     [('find','Find your story'),('form','Draft it')]),
   ('practice-knowledge.html','Trail Tool','Practice Guide: Knowledge Application',"Find your story and draft it, one step at a time.",20,
     [('find','Find your story'),('form','Draft it')]),
   ('practice-choice.html','Trail Tool','Practice Guide: Your Choice',"Choose your skill, then draft your story.",20,
     [('find','Choose your skill'),('form','Draft it')]),
  ]),
 dict(n='I', slug='instructor', label='Instructor Guide', navlabel='Guide', unit='guide', overview='Guide overview', kicker='Part',
  title='Instructor Guide', icon='images/shared/instructor-badge.svg',
  desc="For FYE 100 instructors and reviewers: how the book works, the course map, and how the course aligns to the 10 Essential Skills and AI literacy.",
  tagline="How the book works, and how every piece of the course lines up.",
  intro=["This guide is for FYE 100 instructors, peer reviewers, and anyone reporting on the course. It explains how the book and Blackboard work together and maps every I Can statement to the course learning outcomes, the Kentucky Graduate Profile's 10 Essential Skills, and the BE framework for AI literacy.",
         "The maps are built from the same source as the book, so they grow as modules are completed. Like the rest of the book, this guide is public. It contains no answer keys, scoring guidance, or points. Those stay in Blackboard."],
  lessons=[
   ('how-the-book-works.html','1','How the Book Works',"The book, Blackboard, and how a module is put together.",8,
     [('split','The book and Blackboard'),('anatomy','How a module is built'),('design','Design commitments'),('teaching','Teaching with the book'),('current','Keeping the book current'),('assessment','Course-level assessment'),('reporting','Using the maps')]),
   ('course-map.html','2','Course Map',"Every I Can statement, the outcome it serves, and where students show it.",10,
     [('outcomes','Learning outcomes'),('glance','At a glance'),('modules','Module by module')]),
   ('essential-skills-map.html','3','10 Essential Skills Map',"Kentucky Graduate Profile coverage, by module and by skill.",8,
     [('matrix','Skills by module'),('anchors','Focus skills and anchors'),('skills','Skill by skill')]),
   ('ai-literacy-map.html','4','AI Literacy Map',"The five BE behaviors: where they're taught, practiced, and labeled.",8,
     [('be','The five behaviors'),('matrix','Behaviors by module'),('ican','I Can statements'),('boxes','AI Literacy boxes'),('chats','AI Chats'),('labels','AI use labels')]),
  ]),
]


def ondemand_html():
    out=['          <div class="od-list">']
    for o in MERIT_OPTIONS:
        link = f'\n              <p><a href="{o["link"]}">{o.get("linktext", "Learn more")}</a></p>' if o.get('link') else ''
        out.append(f"""            <article class="od-card">
              <h3>{o['title']}</h3>
              <p class="od-who">{o['who']}</p>
              <p>{o['what']}</p>
              <p><strong>How to find it:</strong> {o['how']}</p>
              <p><strong>Proof:</strong> {o['proof']}</p>{link}
            </article>""")
    out.append('          </div>')
    return '\n'.join(out)

from star_skills import SKILLS as STAR_SKILLS, CHOICE_OPTIONS

def star_practice(s):
    k = s['key']; pre = f'st-{k}'
    def box(step, letter, name, q, coach, watch, rows, label, tr=False):
        cls = ('st-step st-transfer ss-tr' if tr else f'st-step ss-{step}')
        return f"""            <fieldset class="mm-field {cls}">
              <legend><span class="st-letter" aria-hidden="true">{letter}</span><span class="st-name">{name}</span><span class="st-q">{q}</span></legend>
              <p class="st-coach">{coach}</p>
              <label class="sr-only" for="{pre}-{step}">{label}</label>
              <textarea id="{pre}-{step}" data-save data-wc="{k}" data-label="{label}" rows="{rows}"></textarea>
              <p class="st-watch"><strong>Watch out:</strong> {watch}</p>
            </fieldset>"""
    if k == 'choice':
        grid = '\n'.join(f"""              <li><span class="coin-sm"><img src="../../images/shared/10es/10es-{n:02d}.png" alt="" width="160" height="160"><span class="n">{n}</span></span><span><strong>{ESSENTIAL[n]}</strong><span class="cg-desc">{d}</span></span></li>""" for n,d in CHOICE_OPTIONS)
        opts = ''.join(f'<option>#{n} {ESSENTIAL[n]}</option>' for n,_ in CHOICE_OPTIONS)
        find = f"""      <div class="row wide gap-sm">
        <div class="main">
          <ul class="choice-grid">
{grid}
          </ul>
        </div>
      </div>"""
        step0 = f"""            <fieldset class="mm-field">
              <legend><span class="mm-num">Step 0</span>Choose your skill</legend>
              <label class="mm-sub" for="{pre}-skill">My chosen skill</label>
              <select id="{pre}-skill" data-save><option value="">Choose one</option>{opts}</select>
              <label class="mm-sub" for="{pre}-why">Why I chose it, in one or two sentences. Your submission starts with this.</label>
              <textarea id="{pre}-why" data-save rows="2"></textarea>
              <label class="mm-sub" for="{pre}-story">The experience I'm going to use</label>
              <textarea id="{pre}-story" data-save rows="2"></textarea>
            </fieldset>"""
        copypre = f' data-copy-pre="#{pre}-skill, #{pre}-why"'
        head_coin = ''
    else:
        plist = '\n'.join(f'            <li>{x}</li>' for x in s['prompts'])
        find = f"""      <div class="row gap-sm">
        <div class="main">
          <p><strong>Questions to help you find it:</strong></p>
          <ul class="reflect-list st-prompts">
{plist}
          </ul>
        </div>
      </div>"""
        step0 = f"""            <fieldset class="mm-field">
              <legend><span class="mm-num">Step 0</span>Find your story first</legend>
              <label class="mm-sub" for="{pre}-story">The experience I'm going to use</label>
              <textarea id="{pre}-story" data-save rows="2" placeholder="{s['eg']}"></textarea>
            </fieldset>"""
        copypre = ''
        head_coin = f"""          <div class="spotlight st-spot">
            <span class="coin coin-lg"><img src="../../images/shared/10es/10es-{s['n']:02d}.png" alt="" width="160" height="160"><span class="sn">{s['n']}</span></span>
            <div>
              <span class="spot-label">10 Essential Skills · #{s['n']}</span>
              <p class="spot-name">{ESSENTIAL[s['n']]}</p>
            </div>
          </div>
"""
    mm = ''.join(f'<p><a href="{h}">{txt}</a></p>' for h,txt in s['mm'])
    steps = '\n'.join([
      box('s','S','Situation','Set the scene. What was going on?',"Give just enough context for someone who wasn't there. Two or three sentences is usually plenty.","The Situation is the setup, not the story. Get to the Task quickly.",3,'Situation'),
      box('t','T','Task','Define your role. What was yours to do?',s['task'],'Your Task is what you were responsible for, not the group&#39;s general goal.',3,'Task'),
      box('a','A','Action','Show what you did, step by step.',"This is the most important step. Use &quot;I&quot;: I decided, I reached out, I chose. "+s['action'],'"We figured it out" hides your part. Describe what you did, even inside a group effort.',6,'Action'),
      box('r','R','Result','Name the outcome. What happened because of what you did?',s['result'],'"It went well" isn&#39;t a result. Name what specifically happened.',3,'Result'),
      box('tr','T','Transfer','Connect it forward. What does this mean for what comes next?',s['transfer'],'"This will help me in the future" isn&#39;t a Transfer. Name a specific place, role, or situation.',4,'Transfer',True),
    ])
    return f"""    <div class="row gap-md">
      <div class="main">
{head_coin}        <p class="lede">{s['sub']}</p>
        <p>{s['what']}</p>
        <p>This is practice, and it isn't graded. Draft your story here, see how long it runs out loud, then record it or copy it into the matching STAR(T) Stories portal in Blackboard.</p>
      </div>
      <div class="note-col">
        <div class="note note-see">
          <div class="label">[[see]] Look back at</div>
          <p><a href="the-framework.html">The STAR(T) Framework</a></p>
          <p><a href="find-your-stories.html">Find Your Stories</a></p>
        </div>
      </div>
    </div>

    <span class="rest" aria-hidden="true"></span>

    <section id="find" aria-labelledby="find-h">
      <div class="row">
        <div class="main">
          <div class="h2wrap"><h2 id="find-h">{'Choose your skill' if k=='choice' else 'Find your story'}</h2></div>
          <p>{'Read through the options and pick the one you can tell the most specific, honest story about.' if k=='choice' else 'Your story can come from school, work, family, or your community. It doesn&#39;t have to be dramatic. It has to be real, and yours.'}</p>
        </div>
        <div class="note-col">
          <div class="note note-tip">
            <div class="label">[[tip]] Mine your own work</div>
            <p>Your Mile Markers may already hold a story worth telling.</p>{mm}
          </div>
        </div>
      </div>
{find}
    </section>

    <span class="rest" aria-hidden="true"></span>

    <section id="form" aria-labelledby="form-h">
      <div class="row">
        <div class="main">
          <div class="h2wrap"><h2 id="form-h">Draft it, one step at a time</h2></div>
          <p>Your draft saves in this browser as you go. Nothing is sent anywhere.</p>
        </div>
        <div class="note-col">
          <div class="note note-tip">
            <div class="label">[[tip]] Using AI?</div>
            <p>Ask it to help you find your story, not to write it: "Don't write my response for me. Help me find it." Your story has to sound like you.</p>
          </div>
        </div>
      </div>
      <div class="row gap-sm">
        <div class="main">
          <form class="mm-form tool-form st-form" id="mm-form" data-title="{s['pdf']}" novalidate>
            <p class="mm-print-title">{s['pdf'].replace(' - ',': ',1)}</p>
            <div class="mm-id">
              <div class="mm-field">
                <label for="{pre}-name">Your name <span class="req">(required)</span></label>
                <input type="text" id="{pre}-name" data-save autocomplete="name" required aria-describedby="{pre}-name-err">
                <p class="mm-err" id="{pre}-name-err" hidden>Enter your name before saving.</p>
              </div>
              <div class="mm-field">
                <label for="{pre}-date">Date</label>
                <input type="date" id="{pre}-date" data-save>
              </div>
            </div>
{step0}
{steps}
            <div class="wc-box">
              <p class="wc-line">About <span data-wc-time="{k}">0</span> out loud <span class="wc-range">(<output data-wc-total="{k}" data-min="280" data-max="560" data-wpm="140" aria-live="polite">0</output> words; aim for 2 to 4 minutes)</span></p>
              <p class="wc-msg" data-wc-msg aria-live="polite"></p>
            </div>
            <fieldset class="mm-field st-after">
              <legend><span class="mm-num">After you draft it</span>Quick reflection</legend>
              <label class="mm-sub" for="{pre}-hard">Which step was hardest to write, and why do you think that is?</label>
              <textarea id="{pre}-hard" data-save rows="2"></textarea>
              <label class="mm-sub" for="{pre}-generic">Does anything sound generic, like anyone could have written it? Where could you be more specific?</label>
              <textarea id="{pre}-generic" data-save rows="2"></textarea>
            </fieldset>
            <div class="mm-actions">
              <button type="button" class="start-btn" data-copy="{k}" data-copy-labels{copypre} aria-describedby="{pre}-copy-status">Copy my story</button>
              <button type="button" class="mm-save">Save as PDF [[download]]</button>
              <button type="button" class="mm-clear">Clear my answers</button>
            </div>
            <p class="mm-how" id="{pre}-copy-status" aria-live="polite">"Copy my story" copies your five steps, labeled, ready to paste into the STAR(T) Stories portal if you're submitting in writing.</p>
          </form>
        </div>
      </div>
    </section>
"""

def build_guide(g):
    d = ROOT/f'chapters/{g["slug"]}'; d.mkdir(parents=True, exist_ok=True)
    where = g['title']
    for i,(f,num,t,sub,mins,secs) in enumerate(g['lessons']):
        src = g.get('source',{}).get(f, f'{g["slug"]}/{f}')
        bp = HERE/f'bodies/{src}'
        gen = [s for s in STAR_SKILLS if s['file']==f] if g['slug']=='start' else []
        if g['slug']=='instructor' and f in INSTR:
            body = tokens(INSTR[f])
        elif gen:
            body = tokens(star_practice(gen[0]))
        else:
            raw = re.sub(r'<!--ch-only-->.*?<!--/ch-only-->', '', bp.read_text(), flags=re.S) if bp.exists() else ''
            body = tokens(raw.replace('[[ondemand]]', ondemand_html())) if bp.exists() else STUB
        label = num if num in SPECIAL else t
        page = head(f'{t} | {g["title"]} | {BOOK}', 2) + bookbar(2, where) + \
          '\n<div class="shell">\n' + sidebar(g, f) + '\n  <main id="main" class="reading">\n' + crumbs(g, label) + \
          lesson_header(g, i) + '\n' + body + pagenav(g, f) + '  </main>\n</div>\n' + FOOT
        write(d/f, page)
    intro = '\n'.join(f'          <p>{p}</p>' for p in g['intro'])
    cards = []
    for f,num,t,sub,mins,secs in g['lessons']:
        cls = 'lesson-card tip' if num in SPECIAL else 'lesson-card'
        meta = f'<span class="lesson-meta"><span>{ICON["clock"]}About {mins} minutes</span></span>' if mins else ''
        cards.append(f"""          <li>
            <a class="{cls}" href="{f}">
              <span class="lesson-num">{num}</span>
              <div>
                <h3>{t}</h3>
                <p>{sub}</p>
                {meta}
              </div>
            </a>
          </li>""")
    first = g['lessons'][0][0]
    opener = head(f'{g["title"]} | {BOOK}', 2) + bookbar(2, where) + f"""
<div class="banner guide-banner">
  <div class="inner">
    <p class="chapter-kicker"><img class="guide-icon" src="../../{g['icon']}" alt="" width="40" height="40">Guide</p>
    <h1>{g['title']}</h1>
    <p class="tagline">{g['tagline']}</p>
  </div>
  {banner_svg(g['n'])}
</div>

<div class="shell">
""" + sidebar(g, 'index.html') + f"""
  <main id="main" class="reading opener">

    <section aria-labelledby="why" class="row wide gap-sm">
      <div class="main">
        <div class="sticky">
          <h2 id="why">About this guide</h2>
{intro}
        </div>
      </div>
    </section>

    <span class="rest wide" aria-hidden="true"></span>
{g.get('extra','')}
    <section aria-labelledby="lessons" class="row wide">
      <div class="main">
        <div class="h2wrap"><h2 id="lessons">In this guide</h2></div>
        <ol class="lessons">
{chr(10).join(cards)}
        </ol>
        <div class="start-row">
          <a class="start-btn" href="{first}">Start the guide {TOK['next']}</a>
        </div>
      </div>
    </section>

""" + pagenav(g, 'index.html', wide=True) + '  </main>\n</div>\n' + FOOT
    write(d/'index.html', opener)


# ------------------------------------------------------------------ help page
HELP_SECS=[('split','The book and Blackboard'),('module','How each module is laid out'),('save','Keep your work safe'),('ai','AI use labels'),('around','Getting around'),('guides','The guides'),('access','Reading your way')]
def build_help():
    d = ROOT/'chapters/help'; d.mkdir(parents=True, exist_ok=True)
    body = tokens((HERE/'bodies/help/how-to-use.html').read_text())
    toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i,t in HELP_SECS)
    page = head(f'How to Use This Book | {BOOK}', 2) + bookbar(2, 'How to Use This Book') + f"""
<div class="shell solo">
  <main id="main" class="reading">
    <nav class="crumbs" aria-label="Breadcrumb">
      <ol>
        <li><a href="../../index.html">Home</a></li>
        <li><span aria-current="page">How to Use This Book</span></li>
      </ol>
    </nav>
    <div class="row">
      <div class="main">
        <span class="lesson-kicker">Start here</span>
        <h1>How to Use This Book</h1>
        <p class="lesson-sub">How the book and Blackboard fit together, and how to keep your work safe.</p>
      </div>
    </div>
    <div class="row gap-sm"><div class="main"><nav class="page-toc" aria-label="On this page"><span class="pt-label">On this page</span><ul>{toc}</ul></nav></div></div>
""" + body + '  </main>\n</div>\n' + FOOT
    write(d/'index.html', page)

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
    gl = []
    for g in GUIDES:
        gl.append(f'''      <li><a class="guide-card" href="chapters/{g['slug']}/index.html"><img src="{g['icon']}" alt="" width="56" height="56"><span><span class="gc-title">{g['title']}</span><span class="gc-desc">{g['desc']}</span></span></a></li>''')
    home = head(f'{BOOK} | FYE 100: Strategies for College Success', 0) + bookbar(0, '') + f'''
<div class="hero">
  <div class="inner">
    <p class="eyebrow">FYE 100 · Strategies for College Success</p>
    <h1>{BOOK}</h1>
    <p class="tagline">Your guide to college, from your first week to the skills you'll carry with you.</p>
    <a class="start-btn" href="chapters/ch01/index.html">Start reading {TOK['next']}</a>
    <p class="hero-sub"><a href="chapters/help/index.html">New here? How to use this book</a></p>
  </div>
  {banner_svg('START HERE')}
</div>

<main id="main" class="home">
  <p class="home-intro">This guidebook holds the readings for FYE 100. Your course in Blackboard tells you what's due and when. This is where you read, think, and get ready. New to the book? Start with <a href="chapters/help/index.html">How to Use This Book</a>.</p>

  <section aria-labelledby="contents" class="gap-md">
    <div class="h2wrap"><h2 id="contents">Contents</h2></div>
    <ol class="toc">
{chr(10).join(toc)}
    </ol>
  </section>

  <section aria-labelledby="guides" class="gap-md">
    <div class="h2wrap"><h2 id="guides">Guides</h2></div>
    <p class="home-intro">Reference guides you'll use across the whole course. The Instructor Guide is for faculty and course reviewers.</p>
    <ul class="guide-list">
{chr(10).join(gl)}
    </ul>
  </section>
</main>
''' + FOOT
    write(ROOT/'index.html', home)

import instructor
INSTR = instructor.pages(CHAPTERS, LATER, ESSENTIAL, HERE)
for ch in CHAPTERS: build_chapter(ch)
for g in GUIDES: build_guide(g)
build_help()
build_home()
print('built', [c['n'] for c in CHAPTERS])
