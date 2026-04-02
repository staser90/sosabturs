(function () {
  var toggle = document.getElementById('nav-toggle');
  var menu = document.getElementById('nav-menu');
  var backdrop = document.getElementById('nav-backdrop');
  if (!toggle || !menu) return;

  function isMobile() {
    return window.matchMedia('(max-width: 767px)').matches;
  }

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      menu.classList.remove('max-md:hidden');
      menu.classList.add('nav-menu--open');
      if (backdrop) backdrop.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    } else {
      menu.classList.add('max-md:hidden');
      menu.classList.remove('nav-menu--open');
      if (backdrop) backdrop.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }
  }

  toggle.addEventListener('click', function () {
    if (!isMobile()) return;
    var expanded = toggle.getAttribute('aria-expanded') === 'true';
    setOpen(!expanded);
  });

  if (backdrop) {
    backdrop.addEventListener('click', function () {
      setOpen(false);
    });
  }

  document.querySelectorAll('.nav-close').forEach(function (el) {
    el.addEventListener('click', function () {
      if (isMobile()) setOpen(false);
    });
  });

  menu.querySelectorAll('a[href]').forEach(function (el) {
    el.addEventListener('click', function () {
      if (isMobile()) setOpen(false);
    });
  });

  ['cart-toggle', 'logout-btn'].forEach(function (id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('click', function () {
      if (isMobile()) setOpen(false);
    });
  });

  window.addEventListener('resize', function () {
    if (!isMobile()) setOpen(false);
  });
})();
