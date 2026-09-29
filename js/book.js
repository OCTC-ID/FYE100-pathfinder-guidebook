/* FYE 100 Pathfinder Guidebook: small page behaviors
   1. Chapter sidebar: open on wide screens, collapsed ("Lessons" button) on narrow ones.
   2. Highlights the section being read in the sidebar's section list.
   Pages work without this file; it only adds polish. */
(function () {
  // HARD RULE backup: any link that leaves the book opens in a new tab.
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (a.hostname !== location.hostname) { a.target = '_blank'; a.rel = 'noopener'; }
  });

  var d = document.getElementById('chapdetails');
  if (d) {
    var mq = window.matchMedia('(max-width: 900px)');
    var sync = function () { d.open = !mq.matches; };
    sync();
    if (mq.addEventListener) mq.addEventListener('change', sync);
    // On wide screens the sidebar stays open even if its heading is clicked
    var s = d.querySelector('summary');
    if (s) s.addEventListener('click', function (e) { if (!mq.matches) e.preventDefault(); });
  }

  var links = {};
  document.querySelectorAll('.chapnav .sections a[href^="#"]').forEach(function (a) {
    links[a.getAttribute('href').slice(1)] = a;
  });
  if (!Object.keys(links).length || !('IntersectionObserver' in window)) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      Object.keys(links).forEach(function (k) { links[k].classList.remove('on'); links[k].removeAttribute('aria-current'); });
      var a = links[en.target.id];
      if (a) { a.classList.add('on'); a.setAttribute('aria-current', 'location'); }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  Object.keys(links).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) io.observe(el);
  });
})();

/* Mile Marker fill-in forms: autosave in this browser, name required, Save as PDF
   with the file name "Mile Marker #N - Name" (browsers use the page title as the PDF name). */
(function () {
  var form = document.getElementById('mm-form');
  if (!form) return;
  var key = 'pgb:' + location.pathname;
  var fields = form.querySelectorAll('[data-save]');
  var nameEl = form.querySelector('input[required]');
  var errEl = document.getElementById(nameEl.getAttribute('aria-describedby'));
  var data = {};
  try { data = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}

  function save() {
    var o = {};
    for (var i = 0; i < fields.length; i++) o[fields[i].id] = fields[i].value;
    try { localStorage.setItem(key, JSON.stringify(o)); } catch (e) {}
  }
  for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    if (data[f.id] != null) f.value = data[f.id];
    f.addEventListener('input', save);
  }
  var dateEl = form.querySelector('input[type="date"]');
  if (dateEl && !dateEl.value) {
    var d = new Date();
    dateEl.value = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }
  nameEl.addEventListener('input', function () {
    if (nameEl.value.trim()) { errEl.hidden = true; nameEl.removeAttribute('aria-invalid'); }
  });

  // Copy typed answers into plain text blocks so they print in full
  function mirror() {
    for (var i = 0; i < fields.length; i++) {
      var f = fields[i], out = f.nextElementSibling;
      if (!out || !out.classList.contains('mm-out')) {
        out = document.createElement('div');
        out.className = 'mm-out';
        f.parentNode.insertBefore(out, f.nextSibling);
      }
      var v = f.value;
      if (f.type === 'date' && v) { var p = v.split('-'); v = p[1] + '/' + p[2] + '/' + p[0]; }
      out.textContent = v;
    }
  }
  window.addEventListener('beforeprint', mirror);

  var oldTitle = document.title;
  function restore() { document.title = oldTitle; document.body.classList.remove('mm-printing'); }
  window.addEventListener('afterprint', restore);

  form.querySelector('.mm-save').addEventListener('click', function () {
    var name = nameEl.value.trim();
    if (!name) {
      errEl.hidden = false;
      nameEl.setAttribute('aria-invalid', 'true');
      nameEl.focus();
      return;
    }
    mirror();
    document.title = form.getAttribute('data-title') + ' - ' + name;
    document.body.classList.add('mm-printing');
    window.print();
    setTimeout(restore, 1500);
  });

  form.querySelector('.mm-clear').addEventListener('click', function () {
    if (!window.confirm('Clear all of your answers on this page? This cannot be undone.')) return;
    for (var i = 0; i < fields.length; i++) if (fields[i].type !== 'date') fields[i].value = '';
    try { localStorage.removeItem(key); } catch (e) {}
  });
})();

/* Running totals for the money tools (Module 5).
   Inputs with data-amt="g" add up into <output data-sum="g">.
   <output data-left="a-b"> shows total a minus total b, and [data-left-msg] explains it. */
(function () {
  var outs = document.querySelectorAll('[data-sum], [data-left]');
  if (!outs.length) return;
  function num(v) { var n = parseFloat(String(v || '').replace(/[^0-9.\-]/g, '')); return isNaN(n) ? 0 : n; }
  function money(n) {
    var neg = n < 0, a = Math.abs(Math.round(n * 100) / 100);
    var whole = Math.floor(a).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','), cents = Math.round((a - Math.floor(a)) * 100);
    return (neg ? '-$' : '$') + whole + (cents ? '.' + (cents < 10 ? '0' : '') + cents : '');
  }
  function total(g) { var t = 0; document.querySelectorAll('[data-amt="' + g + '"]').forEach(function (i) { t += num(i.value); }); return t; }
  function calc() {
    document.querySelectorAll('[data-sum]').forEach(function (o) { var t = total(o.getAttribute('data-sum')); o.value = o.hasAttribute('data-plain') ? String(Math.round(t * 10) / 10) : money(t); });
    document.querySelectorAll('[data-left]').forEach(function (o) {
      var p = o.getAttribute('data-left').split('-'), left = total(p[0]) - total(p[1]);
      o.value = money(left);
      var box = o.closest('.left-box'), msg = box && box.querySelector('[data-left-msg]');
      if (box) { box.classList.toggle('is-zero', Math.abs(left) < 0.005 && total(p[0]) > 0); box.classList.toggle('is-over', left < -0.004); }
      if (msg) {
        if (total(p[0]) === 0) msg.textContent = 'Start by entering the money coming in this month.';
        else if (Math.abs(left) < 0.005) msg.textContent = 'Every dollar has a job. That is a zero-based budget.';
        else if (left > 0) msg.textContent = 'You still have money without a job. Give it one, even if the job is savings.';
        else msg.textContent = 'You have assigned more than is coming in. Trim a category until this reaches $0.';
      }
    });
  }
  document.addEventListener('input', calc);
  document.querySelectorAll('.mm-clear').forEach(function (b) { b.addEventListener('click', function () { setTimeout(calc, 50); }); });
  calc();
})();
