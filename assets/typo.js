// Русская типографика: короткие слова не остаются висеть в конце строки.
// Работает по текстовым узлам, разметку не трогает.
(function () {
  var NBSP = ' ';
  // предлоги, союзы и частицы, после которых перенос строки выглядит плохо
  var SHORT = /(^|[\s(«"„])([А-Яа-яЁё]{1,2}|как|что|для|при|над|под|про|без|или|его|ее|их|это|не|ни|же|бы|ли)[ ]+/g;
  var SEL = 'h1, h2, h3, h4, p, li, .lead, .sub, .quote, .note, .fact span, .post__sum, blockquote, td';

  function fixNode(node) {
    var t = node.nodeValue;
    if (!t || t.indexOf(' ') === -1) return;
    // два прохода: соседние короткие слова («как в него») regex за раз не ловит
    var out = t;
    for (var i = 0; i < 2; i++) {
      SHORT.lastIndex = 0;
      out = out.replace(SHORT, function (m, pre, word) { return pre + word + NBSP; });
    }
    // число и его единица тоже держатся вместе
    out = out.replace(/(\d)\s+(₸|₽|%|млн|млрд|тыс|тысяч|руб\w*|тенге|лет|года|год|мес\w*|дней|дня)/g,
      function (m, d, unit) { return d + NBSP + unit; });
    if (out !== t) node.nodeValue = out;
  }

  function run(root) {
    root.querySelectorAll(SEL).forEach(function (el) {
      if (el.closest('code, pre, script, style, .mono')) return;
      Array.prototype.forEach.call(el.childNodes, function (n) {
        if (n.nodeType === 3) fixNode(n);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { run(document); });
  } else {
    run(document);
  }
})();
