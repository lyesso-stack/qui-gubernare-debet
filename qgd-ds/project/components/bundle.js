/* @ds-bundle: {"format":4,"namespace":"QGD","components":[]} */
/* Qui gubernare debet : le seul code partagé. Les composants sont du HTML + bundle.css ; ici, la mise en page du treemap. */
(function () {
  // squarify : items [[nom, valeur], …] triés du plus gros au plus petit -> [[item, x, y, l, h], …]
  function squarify(items, x, y, W, H) {
    var out = [], tot = items.reduce(function (s, i) { return s + i[1]; }, 0), k = W * H / tot;
    items = items.map(function (i) { return [i[0], i[1] * k, i[1]]; });
    function worst(row, side) {
      var s = 0, mx = 0, mn = Infinity;
      row.forEach(function (r) { s += r[1]; mx = Math.max(mx, r[1]); mn = Math.min(mn, r[1]); });
      return Math.max(side * side * mx / (s * s), s * s / (side * side * mn));
    }
    while (items.length) {
      var side = Math.min(W, H), row = [items.shift()];
      while (items.length && worst(row.concat([items[0]]), side) <= worst(row, side)) row.push(items.shift());
      var s = row.reduce(function (a, r) { return a + r[1]; }, 0);
      if (W >= H) { var cw = s / H, cy = y; row.forEach(function (r) { out.push([r, x, cy, cw, r[1] / cw]); cy += r[1] / cw; }); x += cw; W -= cw; }
      else { var ch = s / W, cx = x; row.forEach(function (r) { out.push([r, cx, y, r[1] / ch, ch]); cx += r[1] / ch; }); y += ch; H -= ch; }
    }
    return out;
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function md(v) { return v.toFixed(1).replace('.', ',') + ' Md€'; }
  // treemap(el, [[nom, Md€], …], nomSuivi, href) : remplit el (hauteur fixée en CSS) de tuiles .qg-tile
  function treemap(el, items, follow, href) {
    var tot = items.reduce(function (s, m) { return s + m[1]; }, 0);
    el.innerHTML = squarify(items.slice(), 0, 0, el.clientWidth, el.clientHeight).map(function (t) {
      var n = t[0][0], v = t[0][2], b = v >= 50 ? 4 : v >= 20 ? 3 : v >= 5 ? 2 : 1, room = t[3] > 90 && t[4] > 44;
      return '<a class="qg-tile" href="' + esc(href ? href(n) : '#') + '" data-band="' + b + '"' + (n === follow ? ' data-follow' : '') +
        ' style="left:' + t[1] + 'px;top:' + t[2] + 'px;width:' + t[3] + 'px;height:' + t[4] + 'px" title="' + esc(n) + ' : ' + md(v) + '">' +
        (room ? '<b>' + esc(n) + '</b><span>' + md(v) + ' · ' + Math.round(v / tot * 100) + ' %</span>' : '<span class="qg-sr">' + esc(n) + '</span>') + '</a>';
    }).join('');
  }
  window.QGD = { squarify: squarify, treemap: treemap };
})();
