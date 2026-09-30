# Alignment data for the Instructor Guide.
# Source: FYE 100 Course Competency Framework (Fall 2026), FYE 100 AI Literacy Reference,
# and the KY CPE Kentucky Graduate Profile (10 Essential Skills, v2.19.2026).
# Tags are keyed by I Can number. Built modules use the book's objective wording (from CHAPTERS);
# where the book revised an objective, the tags were adjusted and a note is added.
# es: list of skill numbers. star: skill number that is an institutional assessment anchor.

SLOS = {
 1: 'Develop an educational plan that leads to a career path.',
 2: 'Locate and utilize campus resources including information technology tools.',
 3: 'Develop strategies and techniques for personal, academic, and career success.',
}

ANCHORS = [
 dict(slo=1, es=9, what='My STAR(T) Stories (capstone)', where='Module 12', ican=['12.1', '12.2']),
 dict(slo=3, es=6, what='Mile Marker #8: My Career Snapshot', where='Module 8', ican=['8.2']),
]

TAGS = {
 '1.1': dict(clo=[3], es=[1, 6]),
 '1.2': dict(clo=[2], es=[10], note='Evidence is optional practice and does not count in the grade.'),
 '1.3': dict(clo=[1, 3], es=[5]),
 '1.4': dict(clo=[3], es=[10], be=['Safe'], note='Introduces all five BE behaviors. 1.4d (naming the five behaviors) is shown in the BE Check matching quiz in Blackboard.'),
 '2.1': dict(clo=[2, 3], es=[4]),
 '2.2': dict(clo=[2, 3], es=[4, 1]),
 '2.3': dict(clo=[2], es=[4, 9]),
 '2.4': dict(clo=[2, 3], es=[1, 4], be=['Honest', 'Responsible']),
 '3.1': dict(clo=[3], es=[6], be=['Responsible']),
 '3.2': dict(clo=[3], es=[6]),
 '3.3': dict(clo=[3], es=[6, 5]),
 '3.4': dict(clo=[3], es=[6]),
 '4.1': dict(clo=[3], es=[10]),
 '4.2': dict(clo=[2, 3], es=[10], be=['Critical']),
 '4.3': dict(clo=[2, 3], es=[10]),
 '4.4': dict(clo=[2, 3], es=[6, 10], be=['Honest', 'Responsible'],
             note='Book revision: AI creep replaces the AI note-taker objective. AI note-takers are now a Trail Tip.'),
 '4.5': dict(clo=[3], es=[6]),
 '5.1': dict(clo=[3], es=[3]),
 '5.2': dict(clo=[3], es=[3, 6]),
 '5.3': dict(clo=[3], es=[3]),
 '5.4': dict(clo=[3], es=[3], be=['Safe', 'Responsible']),
 '6.1': dict(clo=[1, 3], es=[9], note='Book revision: Career Coach or the O*NET Interest Profiler.'),
 '6.2': dict(clo=[1], es=[9, 10]),
 '6.3': dict(clo=[1, 3], es=[9, 6]),
 '6.4': dict(clo=[1, 2], es=[1, 9]),
 '6.5': dict(clo=[1], es=[9], be=['Responsible', 'Reflective'], note='Practiced through the optional AI prompt on Mile Marker #6. No AI Chat in this module.'),
 '7.1': dict(clo=[3], es=[5]),
 '7.2': dict(clo=[3], es=[5]),
 '7.3': dict(clo=[1, 3], es=[5, 9]),
 '7.4': dict(clo=[3], es=[5], be=['Reflective']),
 '8.1': dict(clo=[1, 3], es=[2, 10]),
 '8.2': dict(clo=[1, 3], es=[6, 2], be=['Critical', 'Responsible'], star=6),
 '8.3': dict(clo=[1], es=[2]),
 '9.1': dict(clo=[3], es=[2]),
 '9.2': dict(clo=[3], es=[2], be=['Critical']),
 '9.3': dict(clo=[1, 3], es=[9, 1]),
 '9.4': dict(clo=[1, 3], es=[9, 2], be=['Reflective']),
 # planned (not yet in the book): wording from the Competency Framework
 '10.1': dict(clo=[3], es=[8]),
 '10.2': dict(clo=[3], es=[8, 4], note='Mile Marker #10 updated to ask for two strengths (was one or two).'),
 '10.3': dict(clo=[3], es=[8], note='Mile Marker #10 updated to ask for three strategies, one tied to a real experience (was two).'),
 '10.4': dict(clo=[3], es=[1, 8], be=['Honest']),
 '11.1': dict(clo=[3], es=[7]),
 '11.2': dict(clo=[3], es=[7, 4]),
 '11.3': dict(clo=[3], es=[7, 5], be=['Responsible', 'Reflective']),
 '11.4': dict(clo=[1, 3], es=[9]),
 '12.1': dict(clo=[1, 3], es=[9], all_es=True, be=['Honest', 'Reflective'], star=9),
 '12.2': dict(clo=[1], es=[9, 1], be=['Reflective'], star=9),
 '12.3': dict(clo=[3], es=[], choice=True),
 '12.4': dict(clo=[3], es=[], all_es=True, be=['Reflective']),
}

# Objectives for modules not yet built into the book (Competency Framework wording).
PLANNED = {
 10: dict(be=['Responsible'], merit=3, objectives=[
   'identify my natural collaboration tendencies using my 16Personalities results and explain how they show up in group work.',
   'name two collaboration strengths and one or two challenges and explain why those challenges happen.',
   'describe three specific strategies that help me work more effectively with others.',
   'articulate in one clear sentence what I need from teammates to do my best work.']),
 11: dict(be=['Responsible', 'Reflective'], objectives=[
   'define community broadly and identify at least one community I already belong to and contribute to.',
   'describe specific ways my everyday actions make a positive impact on the people around me.',
   'connect my strengths and values to one intentional way I want to grow my community impact going forward.',
   'select four experiences from my semester and match each one to an Essential Skill for my STAR(T) Story.']),
 12: dict(be=['Reflective'], objectives=[
   'record four STAR(T) responses, one per selected Essential Skill, that are specific, honest, and clearly structured.',
   'articulate how each skill connects to my future in college, my career, and my life: the Transfer step.',
   'explain my choice of student-selected skill in my own words.',
   'reflect honestly on my growth this semester, what I am taking with me, and what I want to work on next.']),
}

# KY CPE Kentucky Graduate Profile definitions (v2.19.2026)
ES_DEF = {
 1: 'Graduates will communicate effectively by listening, weighing influencing factors, and responding accurately and professionally. They will express their thoughts coherently in writing, orally, and in formal presentations.',
 2: 'Graduates will think critically by evaluating assumptions and assessing information to make informed conclusions. They will also think creatively by combining ideas in original ways or developing new ways of addressing issues.',
 3: 'Graduates will hone their ability to provide solutions guided by data and choose the best methodologies for arriving at informed conclusions.',
 4: 'Graduates will demonstrate both self-awareness and appreciation of people with different perspectives, as well as the ability to collaborate, communicate, and work respectfully with others.',
 5: 'Graduates will accept change and find effective ways to work and thrive in different settings. They will motivate others in the pursuit of a common goal and coach others in the pursuit of this goal.',
 6: 'Graduates will adhere to the code of ethics in their chosen profession and act with honesty and fairness. They will prioritize their tasks, manage their time, take initiative, and demonstrate accountability and reliability.',
 7: 'Graduates will engage in political, social, and other activities to address issues that benefit society.',
 8: 'Graduates will collaborate with colleagues, become effective team members, and manage conflict.',
 9: 'Graduates will articulate and apply the theoretical content of their academic preparation with relevant knowledge and abilities essential to their chosen careers.',
 10: 'Graduates will identify, evaluate, and responsibly use information needed for decision making.',
}
# Planned Skill Spotlights for modules not yet built
PLANNED_SPOTLIGHT = {10: 8, 11: 7}
STAR_ASSIGNED = [5, 6, 9]

# AI Literacy (BE framework, Tier 1 Benchmark)
BE_DEF = [
 ('Safe', 'Recognize AI-generated content and understand basic risks of sharing personal or sensitive information with AI tools.', 'Understanding AI and Data: AI and Data Awareness'),
 ('Honest', 'Disclose AI use when required; understand the difference between AI assistance and your own work.', 'Ethical and Responsible Use: Understand Risks'),
 ('Critical', 'Evaluate AI output: verify information, identify bias, and assess accuracy before using it.', 'Critical Thinking and Judgement: Question AI Output'),
 ('Responsible', 'Make intentional decisions about when and how to use AI to support your learning, not replace your thinking.', 'Ethical and Responsible Use: Understand Risks'),
 ('Reflective', 'Notice how AI use affects your learning process and growth.', 'Human-Centricity, EI, and Creativity: Awareness of Human-AI Interaction'),
]
BE_ANCHOR = {'Critical': [4, 9], 'Reflective': [12]}

# Blackboard AI Chat scenarios (Coach Pathfinder). title=None when the book does not name it.
AI_CHATS = [
 (2, 'Socratic', 'Asking for help and finding campus support', ['Honest', 'Responsible'], 'Who Has Your Back?'),
 (4, 'Socratic', 'SIFT: evaluating AI-generated information', ['Critical'], 'Is This Legit?'),
 (8, 'Socratic', 'Career fit exploration', ['Critical', 'Responsible'], 'What Future Do You Want Your Career to Make Possible?'),
 (9, 'Socratic', 'The 4C Check applied to a real decision', ['Critical'], 'Think It Through'),
]
