// Страницы блога: тема, мобильное меню, фильтр по стране.
(function () {
  var themeBtns = document.querySelectorAll('#themeToggle, #themeToggleMob');

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.body.classList.add('dark');
      document.querySelectorAll('.theme-toggle-icon-sun').forEach(function (el) { el.style.display = 'none'; });
      document.querySelectorAll('.theme-toggle-icon-moon').forEach(function (el) { el.style.display = ''; });
    } else {
      document.body.classList.remove('dark');
      document.querySelectorAll('.theme-toggle-icon-sun').forEach(function (el) { el.style.display = ''; });
      document.querySelectorAll('.theme-toggle-icon-moon').forEach(function (el) { el.style.display = 'none'; });
    }
    var metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) metaTheme.setAttribute('content', theme === 'dark' ? '#171410' : '#F5F2EA');
  }

  var currentTheme = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(currentTheme);

  themeBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', currentTheme);
      applyTheme(currentTheme);
    });
  });

  var burger = document.getElementById('burger');
  if (burger) burger.addEventListener('click', function () {
    document.body.classList.toggle('menu-open');
  });

  // пилюля в сайдбаре под активным пунктом
  var bubble = document.getElementById('menuBubble');
  var menu = document.getElementById('sbMenu');
  function moveBubble() {
    if (!bubble || !menu) return;
    var act = menu.querySelector('a.is-active');
    if (!act) { bubble.style.opacity = 0; return; }
    bubble.style.opacity = 1;
    bubble.style.top = act.offsetTop + 'px';
    bubble.style.height = act.offsetHeight + 'px';
  }
  moveBubble();
  window.addEventListener('resize', moveBubble);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(moveBubble);

  // фильтр списка разборов по стране
  var filters = document.querySelectorAll('.filter');
  var posts = document.querySelectorAll('.post');
  filters.forEach(function (f) {
    f.addEventListener('click', function () {
      var val = f.dataset.filter;
      filters.forEach(function (x) { x.classList.toggle('is-on', x === f); });
      posts.forEach(function (p) {
        p.style.display = (val === 'all' || p.dataset.region === val) ? '' : 'none';
      });
    });
  });

  // полоса прочитанного на странице разбора
  var bar = document.querySelector('.progress__bar');
  var article = document.querySelector('.article__body');
  if (bar && article) {
    var ticking = false;
    var update = function () {
      var box = article.getBoundingClientRect();
      var start = window.scrollY + box.top;
      var passed = window.scrollY + window.innerHeight * 0.75 - start;
      var pct = Math.max(0, Math.min(1, passed / box.height));
      bar.style.width = (pct * 100).toFixed(1) + '%';
      ticking = false;
    };
    var onScroll = function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
  }

  // появление при прокрутке
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('rv-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });
  }
})();
