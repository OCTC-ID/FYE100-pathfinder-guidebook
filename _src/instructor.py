# Generated pages for the Instructor Guide: Course Map, 10 Essential Skills Map, AI Literacy Map.
# Everything is computed from CHAPTERS / LATER in build2.py plus alignment.py, so the maps
# update whenever a module is built or revised.
import re
from alignment import (SLOS, ANCHORS, TAGS, PLANNED, ES_DEF, PLANNED_SPOTLIGHT, STAR_ASSIGNED,
                       BE_DEF, BE_ANCHOR, AI_CHATS)

BE_ORDER = [b[0] for b in BE_DEF]
STAR = '<span class="anchor-star" title="Institutional assessment anchor">★<span class="sr-only"> Institutional assessment anchor</span></span>'
DOT = '<span class="mx on" aria-hidden="true">●</span>'
SPOT = '<span class="mx spot" aria-hidden="true">◆</span>'


def clean(t):
    return re.sub('<[^>]+>', '', t)


def print_btn():
    return '''    <div class="row wide"><div class="main">
      <p class="map-actions"><button type="button" class="print-btn" onclick="window.print()">Print this map</button> <span>Or save it as a PDF from the print window.</span></p>
    </div></div>
'''


class Course:
    """A flat view of every module: built ones from CHAPTERS, planned ones from LATER + PLANNED."""
    def __init__(self, CHAPTERS, LATER, ESSENTIAL, HERE):
        self.E = ESSENTIAL; self.HERE = HERE; self.mods = []
        for ch in CHAPTERS:
            n = ch['n']
            spot = None
            for f, num, t, *_ in ch['lessons']:
                if t.startswith('Skill Spotlight:'):
                    name = t.split(':', 1)[1].strip()
                    spot = next((k for k, v in ESSENTIAL.items() if v == name), None)
                    spot = (spot, f, num, t)
            objs = []
            for i, (txt, mark) in enumerate(ch['objectives']):
                key = f'{n}.{i+1}'
                objs.append(dict(key=key, text=txt, mark=mark, **self._tag(key)))
            tools = [(f, t) for f, num, t, *_ in ch['lessons'] if num == 'Trail Tool']
            tips = [(f, t) for f, num, t, *_ in ch['lessons'] if num == 'Trail Tip']
            mm = next(((f, t) for f, num, t, *_ in ch['lessons'] if num == 'Mile Marker'), None)
            label = None
            bp = HERE / f'bodies/ch{n:02d}/mile-marker.html'
            if bp.exists():
                m = re.search(r'AI use: ([^<]+)', bp.read_text())
                label = m.group(1).strip() if m else None
            self.mods.append(dict(n=n, title=ch['title'], built=True, objs=objs, be=ch['be'], merit=ch.get('merit'),
                                  spot=spot, tools=tools, tips=tips, mm=mm, ai_label=label,
                                  lessons=ch['lessons'], es=ch['es']))
        for n, t, dsc in LATER:
            p = PLANNED.get(n, dict(objectives=[], be=[]))
            objs = [dict(key=f'{n}.{i+1}', text=txt, mark=None, **self._tag(f'{n}.{i+1}')) for i, txt in enumerate(p['objectives'])]
            sp = PLANNED_SPOTLIGHT.get(n)
            self.mods.append(dict(n=n, title=t, built=False, objs=objs, be=p.get('be', []), merit=p.get('merit'),
                                  spot=(sp, None, None, None) if sp else None, tools=[], tips=[], mm=None, ai_label=None,
                                  lessons=[], es=[]))

    def _tag(self, key):
        t = TAGS.get(key, {})
        return dict(clo=t.get('clo', []), tes=t.get('es', []), tbe=t.get('be', []), star=t.get('star'),
                    note=t.get('note'), all_es=t.get('all_es'), choice=t.get('choice'))

    # -- small renderers
    def es_tag(self, k, star=None):
        s = STAR if star == k else ''
        return f'<span class="es-tag"><span class="es-n">{k}</span>{self.E[k]}{s}</span>'

    def es_cell(self, o):
        parts = [self.es_tag(k, o['star']) for k in o['tes']]
        if o['all_es']: parts.insert(0, '<span class="es-tag es-all">All 10 skills</span>')
        if o['choice']: parts.append('<span class="es-tag es-all">Student choice</span>')
        return ' '.join(parts) or '<span class="muted">None tagged</span>'

    @staticmethod
    def be_cell(bes):
        return ' '.join(f'<span class="be-chip">BE {b}</span>' for b in bes) or '<span class="muted">—</span>'

    @staticmethod
    def evidence(o, n):
        m = o['mark']
        if isinstance(m, str) and m.startswith('Mile Marker'):
            return f'<a href="../ch{n:02d}/mile-marker.html">{m}</a>'
        if isinstance(m, str):
            m = re.sub(r'^the ', '', m)
            return m[0].upper() + m[1:]
        if m is True:
            return 'Lesson practice and course activities'
        if m is False:
            return 'Lessons and course activities'
        return '<span class="muted">Planned</span>'

    def mod_link(self, m, text=None):
        text = text or f'Module {m["n"]}'
        return f'<a href="../ch{m["n"]:02d}/index.html">{text}</a>' if m['built'] else text


def status(m):
    return '' if m['built'] else ' <span class="planned-tag">Planned</span>'


# ---------------------------------------------------------------- Course Map
def course_map(C):
    E = C.E; out = []
    PLANNED_NOTE = ' Modules still in development are marked <span class="planned-tag">Planned</span> and use the Framework as written.' if any(not m['built'] for m in C.mods) else ''
    out.append('''    <div class="row gap-md">
      <div class="main">
        <p class="lede">Every "I Can" statement in FYE 100, with the outcome it serves, the skills and behaviors it builds, and where students show it.</p>
        <p>Objectives use the book's wording, which follows the Competency Framework.{PLANNED_NOTE} A <span class="anchor-star">★</span> marks an institutional assessment anchor: an I Can statement that generates evidence for SLO reporting.</p>
      </div>
    </div>
''' + print_btn() + '''
    <span class="rest" aria-hidden="true"></span>
''')
    # outcomes
    rows = []
    for s, txt in SLOS.items():
        hits = [(m, o) for m in C.mods for o in m['objs'] if s in o['clo']]
        mods = sorted({m['n'] for m, o in hits})
        rows.append(f'<tr><th scope="row">CLO {s}</th><td>{txt}</td><td class="num">{len(hits)}</td><td>{", ".join(map(str, mods))}</td></tr>')
    anc = ''.join(
        f'<li>{STAR} <strong>SLO {a["slo"]}</strong> is assessed through <strong>#{a["es"]} {E[a["es"]]}</strong> in {a["what"]} ({a["where"]}, I Can {" and ".join(a["ican"])}).</li>'
        for a in ANCHORS)
    out.append(f'''    <section id="outcomes" aria-labelledby="out-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="out-h">Course learning outcomes</h2></div>
        <p>How many I Can statements serve each course learning outcome (CLO), and in which modules. Many statements serve more than one.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="Course learning outcomes" tabindex="0">
        <table class="map-table">
          <caption class="sr-only">Course learning outcomes and I Can coverage</caption>
          <thead><tr><th scope="col">CLO</th><th scope="col">Outcome</th><th scope="col" class="num">I Can statements</th><th scope="col">Modules</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
        <h3 class="sub-h">Institutional assessment anchors</h3>
        <ul class="dots anchors">{anc}</ul>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # at a glance
    rows = []
    for m in C.mods:
        es = sorted({k for o in m['objs'] for k in o['tes']})
        sp = m['spot'][0] if m['spot'] else None
        es = sorted(set(es) | ({sp} if sp else set()))
        es_txt = ', '.join(f'<strong>{k}</strong>' if k == sp else str(k) for k in es) or '—'
        mm = f'<a href="../ch{m["n"]:02d}/{m["mm"][0]}">{m["mm"][1].split(":")[0]}</a>' if m['mm'] else f'Mile Marker #{m["n"]}' if m['n'] < 12 else 'STAR(T) Stories'
        tools = ', '.join(f'<a href="../ch{m["n"]:02d}/{f}">{t}</a>' for f, t in m['tools']) or '—'
        merit = f'Merit #{m["merit"]}' if m['merit'] else '—'
        rows.append(f'<tr{"" if m["built"] else " class=planned"}><th scope="row">{C.mod_link(m, str(m["n"]))}</th><td>{m["title"]}{status(m)}</td><td>{es_txt}</td><td>{C.be_cell(m["be"])}</td><td class="nowrap">{mm}</td><td>{tools}</td><td class="nowrap">{merit}</td></tr>')
    out.append(f'''    <section id="glance" aria-labelledby="gl-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="gl-h">The course at a glance</h2></div>
        <p>Essential Skills are listed by number. The number in bold is that module's Skill Spotlight.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="Course at a glance" tabindex="0">
        <table class="map-table glance">
          <caption class="sr-only">Modules with Essential Skills, AI Literacy behaviors, Mile Markers, Trail Tools, and Merit activities</caption>
          <thead><tr><th scope="col">Module</th><th scope="col">Title</th><th scope="col">10 Essential Skills</th><th scope="col">AI Literacy</th><th scope="col">Main assignment</th><th scope="col">Trail Tools</th><th scope="col">Merit</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # module by module
    blocks = []
    for m in C.mods:
        rows = []
        for o in m['objs']:
            clo = ', '.join(f'CLO {c}' for c in o['clo'])
            note = f'<span class="map-note">{o["note"]}</span>' if o['note'] else ''
            star = STAR if o['star'] else ''
            rows.append(f'<tr><th scope="row">{o["key"]}</th><td><strong>I can</strong> {o["text"]}{star}{note}</td><td class="nowrap">{clo}</td><td>{C.es_cell(o)}</td><td>{C.be_cell(o["tbe"])}</td><td>{C.evidence(o, m["n"])}</td></tr>')
        extras = []
        if m['spot'] and m['spot'][1]:
            extras.append(f'Skill Spotlight: <a href="../ch{m["n"]:02d}/{m["spot"][1]}">{E[m["spot"][0]]}</a>')
        elif m['spot']:
            extras.append(f'Skill Spotlight: {E[m["spot"][0]]} (planned)')
        if m['tips']:
            extras.append('Trail Tips: ' + ', '.join(f'<a href="../ch{m["n"]:02d}/{f}">{t}</a>' for f, t in m['tips']))
        if m['ai_label']:
            extras.append(f'Mile Marker AI use: {m["ai_label"]}')
        if m['merit']:
            extras.append(f'Merit Activity #{m["merit"]} due with this module')
        ex = ''.join(f'<li>{x}</li>' for x in extras)
        blocks.append(f'''      <div class="map-mod{'' if m['built'] else ' planned'}">
        <h3 id="m{m['n']}">{C.mod_link(m)}: {m['title']}{status(m)}</h3>
        {f'<ul class="map-extras">{ex}</ul>' if ex else ''}
        <div class="table-scroll" role="region" aria-label="Module {m['n']} I Can statements" tabindex="0">
        <table class="map-table ican">
          <caption class="sr-only">Module {m['n']} I Can statements and alignment</caption>
          <thead><tr><th scope="col">#</th><th scope="col">I Can statement</th><th scope="col">CLO</th><th scope="col">10 Essential Skills</th><th scope="col">AI Literacy</th><th scope="col">Where students show it</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div>''')
    out.append(f'''    <section id="modules" aria-labelledby="mods-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="mods-h">Module by module</h2></div>
        <p>"Where students show it" names the book's Mile Marker or the Blackboard activity tied to each statement. Statements marked "Lesson practice" are practiced in the lessons and course activities rather than a single graded piece.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
{chr(10).join(blocks)}
      </div></div>
    </section>
''')
    return ''.join(out).replace('{PLANNED_NOTE}', PLANNED_NOTE)


# ---------------------------------------------------------------- 10 Essential Skills
def es_map(C):
    E = C.E; out = []
    head_cells = ''.join(
        f'<th scope="col" class="mx-h"><span class="coin-xs"><img src="../../images/shared/10es/10es-{k:02d}.png" alt="" width="160" height="160"></span><span class="mx-num">{k}</span><span class="sr-only"> {E[k]}</span></th>'
        for k in E)
    rows = []; totals = {k: 0 for k in E}
    for m in C.mods:
        tagged = {k for o in m['objs'] for k in o['tes']}
        for o in m['objs']:
            for k in o['tes']: totals[k] += 1
        sp = m['spot'][0] if m['spot'] else None
        cells = []
        for k in E:
            c = []
            if k in tagged: c.append(DOT)
            if k == sp: c.append(SPOT)
            sr = []
            if k in tagged: sr.append('I Can aligned')
            if k == sp: sr.append('Skill Spotlight')
            cells.append(f'<td class="mx-c">{"".join(c)}<span class="sr-only">{", ".join(sr) or "—"}</span></td>')
        rows.append(f'<tr{"" if m["built"] else " class=planned"}><th scope="row">{C.mod_link(m, str(m["n"]))}<span class="mx-title">{clean(m["title"]).split(" — ")[0]}{status(m)}</span></th>{"".join(cells)}</tr>')
    tot = ''.join(f'<td class="mx-c">{totals[k]}</td>' for k in E)
    out.append(f'''    <div class="row gap-md">
      <div class="main">
        <p class="lede">How FYE 100 introduces and builds all ten skills in the Kentucky Graduate Profile.</p>
        <p>The Kentucky Council on Postsecondary Education (CPE) defines 10 Essential Skills every graduate should be able to show. FYE 100 introduces all ten in <a href="../ch01/1-2.html">Lesson 1.2</a>, gives most of them a Skill Spotlight lesson, and has students tell the story of four of them in the STAR(T) Stories capstone. Learn more on the <a href="https://cpe.ky.gov/ourwork/kygradprofile.html">Kentucky Graduate Profile</a> page.</p>
      </div>
    </div>
''' + print_btn() + f'''
    <span class="rest" aria-hidden="true"></span>

    <section id="matrix" aria-labelledby="mx-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="mx-h">Skills by module</h2></div>
        <p class="legend"><span>{DOT} An I Can statement is aligned to this skill</span> <span>{SPOT} Skill Spotlight lesson</span></p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="Skills by module" tabindex="0">
        <table class="map-table matrix">
          <caption class="sr-only">10 Essential Skills by module</caption>
          <thead><tr><th scope="col">Module</th>{head_cells}</tr></thead>
          <tbody>{"".join(rows)}</tbody>
          <tfoot><tr><th scope="row">I Can statements</th>{tot}</tr></tfoot>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    anc = ''.join(
        f'<li>{STAR} <strong>#{a["es"]} {E[a["es"]]}</strong> is the evidence for <strong>SLO {a["slo"]}</strong>: {a["what"]} ({a["where"]}, I Can {" and ".join(a["ican"])}).</li>'
        for a in ANCHORS)
    out.append(f'''    <section id="anchors" aria-labelledby="an-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="an-h">Course focus skills and anchors</h2></div>
        <p>Two skills carry the course's institutional assessment. Both are also assigned STAR(T) Stories, along with Adaptability &amp; Leadership. Students choose their fourth story skill.</p>
        <ul class="dots anchors">{anc}</ul>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    cards = []
    for k in E:
        sp = [(m, m['spot']) for m in C.mods if m['spot'] and m['spot'][0] == k]
        if sp:
            m, s = sp[0]
            sp_txt = f'<a href="../ch{m["n"]:02d}/{s[1]}">Lesson {s[2]}</a> (Module {m["n"]})' if s[1] else f'Module {m["n"]} (planned)'
        else:
            sp_txt = ''
        items = [f'<li><span class="ic-key">{o["key"]}</span> I can {o["text"]}{STAR if o["star"] == k else ""}{status(m) if not m["built"] else ""}</li>'
                 for m in C.mods for o in m['objs'] if k in o['tes']]
        star_role = 'Assigned STAR(T) Story' if k in STAR_ASSIGNED else 'Student-choice STAR(T) Story option'
        meta = [f'<li><strong>Skill Spotlight:</strong> {sp_txt}</li>' if sp_txt else '<li><strong>Skill Spotlight:</strong> <span class="muted">none</span></li>',
                f'<li><strong>Capstone:</strong> {star_role}</li>']
        cards.append(f'''        <article class="es-card" id="es{k}" aria-labelledby="es{k}-h">
          <div class="es-card-head">
            <span class="coin-sm"><img src="../../images/shared/10es/10es-{k:02d}.png" alt="" width="160" height="160"><span class="n">{k}</span></span>
            <h3 id="es{k}-h">{E[k]}</h3>
          </div>
          <p class="es-def">{ES_DEF[k]}</p>
          <ul class="es-meta">{"".join(meta)}</ul>
          <p class="es-sub">I Can statements ({len(items)})</p>
          <ul class="es-ican">{"".join(items) or '<li class="muted">None tagged yet</li>'}</ul>
        </article>''')
    out.append(f'''    <section id="skills" aria-labelledby="sk-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="sk-h">Skill by skill</h2></div>
        <p>Each skill with its CPE definition, where it gets its own lesson, and every I Can statement aligned to it.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="es-cards">
{chr(10).join(cards)}
        </div>
        <p class="source-note">Skill definitions: Kentucky Council on Postsecondary Education, Kentucky Graduate Profile.</p>
      </div></div>
    </section>
''')
    return ''.join(out)


# ---------------------------------------------------------------- AI Literacy
def ai_map(C):
    out = []
    defs = ''.join(f'<tr><th scope="row"><span class="be-chip">BE {b}</span></th><td>{d}</td><td>{dec}</td></tr>' for b, d, dec in BE_DEF)
    # matrix
    head_cells = ''.join(f'<th scope="col" class="mx-h">{b}</th>' for b in BE_ORDER)
    rows = []
    for m in C.mods:
        tagged = {b for o in m['objs'] for b in o['tbe']}
        cells = []
        for b in BE_ORDER:
            c = []; sr = []
            if b in m['be']: c.append(DOT); sr.append('Module focus')
            if b in tagged: c.append(SPOT); sr.append('I Can statement')
            if m['n'] in BE_ANCHOR.get(b, []): c.append('<span class="mx star" aria-hidden="true">★</span>'); sr.append('Anchor module')
            cells.append(f'<td class="mx-c">{"".join(c)}<span class="sr-only">{", ".join(sr) or "—"}</span></td>')
        rows.append(f'<tr{"" if m["built"] else " class=planned"}><th scope="row">{C.mod_link(m, str(m["n"]))}<span class="mx-title">{clean(m["title"]).split(" — ")[0]}{status(m)}</span></th>{"".join(cells)}</tr>')
    out.append(f'''    <div class="row gap-md">
      <div class="main">
        <p class="lede">How FYE 100 builds AI literacy: five observable behaviors, taught in the lessons, practiced in AI Chats, and labeled on every assignment.</p>
        <p>The course uses the BE framework, a student-facing, behavioral translation of the Digital Education Council (DEC) AI Literacy Framework used at the KCTCS system level. FYE 100 covers Tier 1 (Benchmark), which maps to DEC Level 1. The framing question across the course: <em>How do students make intentional decisions about using AI while maintaining ownership of their learning?</em></p>
        <p>AI use is never required. Every behavior is framed around judgment, including the decision not to use AI.</p>
      </div>
    </div>
''' + print_btn() + f'''
    <span class="rest" aria-hidden="true"></span>

    <section id="be" aria-labelledby="be-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="be-h">The five BE behaviors</h2></div>
        <p>All five are introduced in <a href="../ch01/1-3.html">Lesson 1.3</a> and <a href="../ch01/1-4.html">Lesson 1.4</a>. Be Safe and Be Honest are baseline expectations from Module 1 on. Be Critical, Be Responsible, and Be Reflective recur as course anchors.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="BE behaviors" tabindex="0">
        <table class="map-table">
          <caption class="sr-only">BE behaviors, what they mean at Tier 1, and the DEC dimension each translates</caption>
          <thead><tr><th scope="col">Behavior</th><th scope="col">What it means at Tier 1</th><th scope="col">DEC dimension: Level 1</th></tr></thead>
          <tbody>{defs}</tbody>
        </table>
        </div>
        <p class="source-note">DEC Dimension 5, Domain Expertise, is intentionally out of scope for FYE 100. It belongs to Tier 2 program courses.</p>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>

    <section id="matrix" aria-labelledby="mx-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="mx-h">Behaviors by module</h2></div>
        <p class="legend"><span>{DOT} Module focus</span> <span>{SPOT} Tagged on an I Can statement</span> <span><span class="mx star" aria-hidden="true">★</span> Primary anchor module</span></p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="Behaviors by module" tabindex="0">
        <table class="map-table matrix be-matrix">
          <caption class="sr-only">BE behaviors by module</caption>
          <thead><tr><th scope="col">Module</th>{head_cells}</tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # I Can with BE
    rows = [f'<tr{"" if m["built"] else " class=planned"}><th scope="row">{o["key"]}</th><td><strong>I can</strong> {o["text"]}{status(m) if not m["built"] else ""}</td><td>{C.be_cell(o["tbe"])}</td><td>{C.evidence(o, m["n"])}</td></tr>'
            for m in C.mods for o in m['objs'] if o['tbe']]
    out.append(f'''    <section id="ican" aria-labelledby="ic-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="ic-h">I Can statements with an AI Literacy behavior</h2></div>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="I Can statements with AI Literacy behaviors" tabindex="0">
        <table class="map-table">
          <caption class="sr-only">I Can statements tagged with a BE behavior</caption>
          <thead><tr><th scope="col">#</th><th scope="col">I Can statement</th><th scope="col">Behavior</th><th scope="col">Where students show it</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # AI boxes, scanned from the lesson files
    rows = []
    for m in C.mods:
        if not m['built']: continue
        for f, num, t, *_ in m['lessons']:
            bp = C.HERE / f'bodies/ch{m["n"]:02d}/{f}'
            if not bp.exists(): continue
            for lab in re.findall(r'class="ai-box-label">(.*?)</p>', bp.read_text(), re.S):
                chips = re.findall(r'BE (\w+)', lab)
                name = t if num in ('Trail Tip', 'Trail Tool', 'Mile Marker') else f'{num} {t}'
                kind = f'{num}: ' if num in ('Trail Tip', 'Trail Tool') else 'Lesson '
                rows.append(f'<tr><th scope="row">{m["n"]}</th><td><a href="../ch{m["n"]:02d}/{f}">{kind}{name}</a></td><td>{C.be_cell(chips)}</td></tr>')
    out.append(f'''    <section id="boxes" aria-labelledby="bx-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="bx-h">AI Literacy boxes in the lessons</h2></div>
        <p>Lessons carry short AI Literacy boxes that apply the module's topic to AI, tagged with the behavior they build. This list updates as modules are added.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="AI Literacy boxes" tabindex="0">
        <table class="map-table">
          <caption class="sr-only">AI Literacy boxes by lesson</caption>
          <thead><tr><th scope="col">Module</th><th scope="col">Where</th><th scope="col">Behavior</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # AI chats
    built = {m['n'] for m in C.mods if m['built']}
    rows = [f'<tr{"" if n in built else " class=planned"}><th scope="row">{n}</th><td>{typ}</td><td>{topic}{f"<span class=map-note>&ldquo;{title}&rdquo;</span>" if title else ""}</td><td>{C.be_cell(bes)}</td></tr>'
            for n, typ, topic, bes, title in AI_CHATS]
    out.append(f'''    <section id="chats" aria-labelledby="ch-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="ch-h">Blackboard AI Chats</h2></div>
        <p>{['No','One','Two','Three','Four','Five','Six','Seven','Eight'][len(AI_CHATS)]} modules include an AI Chat with Coach Pathfinder in Blackboard. Each one is Socratic: Coach Pathfinder asks questions instead of giving answers, so the thinking stays with the student.</p>
      </div></div>
      <div class="row wide gap-sm"><div class="main">
        <div class="table-scroll" role="region" aria-label="AI Chats" tabindex="0">
        <table class="map-table">
          <caption class="sr-only">Blackboard AI Chat scenarios by module</caption>
          <thead><tr><th scope="col">Module</th><th scope="col">Type</th><th scope="col">Topic</th><th scope="col">Behavior</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        </div>
      </div></div>
    </section>

    <span class="rest" aria-hidden="true"></span>
''')
    # AI use labels
    labs = [f'<li><a href="../ch{m["n"]:02d}/{m["mm"][0]}">{clean(m["mm"][1])}</a>: <strong>{m["ai_label"] or "not labeled"}</strong></li>'
            for m in C.mods if m['built'] and m['mm']]
    out.append(f'''    <section id="labels" aria-labelledby="lb-h">
      <div class="row"><div class="main">
        <div class="h2wrap"><h2 id="lb-h">AI use labels on assignments</h2></div>
        <p>Students learn three levels of AI use in <a href="../ch01/1-4.html">Lesson 1.4</a>: <strong>No AI</strong>, <strong>AI-supported</strong>, and <strong>AI-integrated</strong>. Levels are set assignment by assignment, and every Mile Marker in the book carries its label.</p>
        <ul class="dots">{"".join(labs)}</ul>
        <p>Students also have the <a href="https://octc-id.github.io/student-ai-use-guide/index.html">Using AI in Your Coursework</a> guide, linked from Lesson 1.4.</p>
      </div></div>
    </section>
''')
    return ''.join(out)


def pages(CHAPTERS, LATER, ESSENTIAL, HERE):
    C = Course(CHAPTERS, LATER, ESSENTIAL, HERE)
    return {'course-map.html': course_map(C), 'essential-skills-map.html': es_map(C), 'ai-literacy-map.html': ai_map(C)}
