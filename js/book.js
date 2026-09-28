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
