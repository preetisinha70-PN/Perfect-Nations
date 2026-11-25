/* The three mandates, v2.2: shared on request. "Request access" opens a dialog that writes to
   contact@perfectnations.com from the visitor's own email (mail app, Gmail or Outlook), or copies the address.
   Nothing is stored on the site. Without dialog support or without this script, the link opens the email itself.
   Written without angle brackets or a literal ampersand, so the WordPress formatter leaves it alone. */
(function () {
  var R = document.getElementById('ROOT');
  if (!R) { return; }
  var dlg = R.querySelector('.md-dlg');
  if (!dlg) { return; }
  var TO = 'contact@perfectnations.com', AMP = String.fromCharCode(38);
  var SUBJ = dlg.getAttribute('data-subject') || 'Request';
  var WHAT = dlg.getAttribute('data-what') || 'the full mandate';
  function val(n) { var e = dlg.querySelector('[name="' + n + '"]'); return e ? e.value.replace(/^\s+|\s+$/g, '') : ''; }
  function body() {
    var t = ['Dear Perfect Nations,', '', 'I would like to receive ' + WHAT + '.', ''];
    if (val('why')) { t.push(val('why'), ''); }
    t.push('Name: ' + val('name'), 'Organisation and role: ' + val('org'));
    return t.join('\n');
  }
  function set(v, u) { var a = dlg.querySelector('[data-via="' + v + '"]'); if (a) { a.href = u; } }
  function links() {
    var s = encodeURIComponent(SUBJ), b = encodeURIComponent(body());
    set('mail', 'mailto:' + TO + '?subject=' + s + AMP + 'body=' + b);
    set('gmail', 'https://mail.google.com/mail/?view=cm' + AMP + 'fs=1' + AMP + 'to=' + TO + AMP + 'su=' + s + AMP + 'body=' + b);
    set('outlook', 'https://outlook.office.com/mail/deeplink/compose?to=' + TO + AMP + 'subject=' + s + AMP + 'body=' + b);
  }
  function open(e) {
    if (typeof dlg.showModal !== 'function') { return; }
    e.preventDefault();
    links();
    dlg.showModal();
    var f = dlg.querySelector('input');
    if (f) { f.focus(); }
  }
  Array.prototype.forEach.call(R.querySelectorAll('.md-ask'), function (a) { a.addEventListener('click', open); });
  dlg.addEventListener('input', links);
  var x = dlg.querySelector('.md-dlg__x');
  if (x) { x.addEventListener('click', function () { dlg.close(); }); }
  dlg.addEventListener('click', function (e) { if (e.target === dlg) { dlg.close(); } });
  var cp = dlg.querySelector('[data-via="copy"]');
  if (cp) {
    cp.addEventListener('click', function () {
      function done() { cp.textContent = 'Copied'; }
      if (navigator.clipboard) { navigator.clipboard.writeText(TO).then(done, function () { cp.textContent = TO; }); }
      else { cp.textContent = TO; }
    });
  }
})();
