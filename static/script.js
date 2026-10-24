// Авто-закрытие flash-сообщений + анимированный фон с кодом
document.addEventListener('DOMContentLoaded', function() {
    var alerts = document.querySelectorAll('.alert-dismissible');
    setTimeout(function() {
        alerts.forEach(function(alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    initCodeBackground();
});

// ---- Анимированный фон: колонки с примерами решения задач (в т.ч. ЕГЭ) ----
var CODE_SNIPPETS = [
    "# ЕГЭ информатика, задание 1\ns = 0\nn = 0\nwhile s < 111:\n    s = s + 7\n    n = n + 1\nprint(n)   # 16",
    "# Поиск кратных чисел\ncount = 0\nfor i in range(100, 1000):\n    if i % 5 == 0 and i % 11 != 0:\n        count += 1\nprint(count)",
    "# Сумма цифр числа\nn = 12345\ns = 0\nwhile n > 0:\n    s += n % 10\n    n //= 10\nprint(s)",
    "# Рекурсия как в ЕГЭ\ndef f(x):\n    if x < 2:\n        return 1\n    if x % 2 == 0:\n        return f(x - 2) + 1\n    return f(x - 1)\nprint(f(10))",
    "# Цикл с шагом\nfor i in range(2, 101, 2):\n    print(i, end=' ')\n# 2 4 6 ... 100",
    "# Вложенные условия\nx = 15\nif x > 10:\n    if x % 3 == 0:\n        print('>10 и кратно 3')",
    "# Двоичное представление\nn = 42\nb = bin(n)[2:]\nprint(b)            # 101010\nprint(b.count('1')) # 3",
    "# Максимум в списке\narr = [3, 1, 4, 1, 5]\nm = arr[0]\nfor v in arr:\n    if v > m:\n        m = v\nprint(m)",
    "# Простые числа\nfor k in range(2, 40):\n    ok = True\n    for d in range(2, int(k**0.5) + 1):\n        if k % d == 0:\n            ok = False\n            break\n    if ok:\n        print(k, end=' ')",
    "# while и break\ni = 1\nwhile True:\n    if i * i > 200:\n        break\n    i += 1\nprint(i)",
    "# Строки\ns = 'информатика'\nprint(s.upper())\nprint(s[::-1])\nprint(len(s))",
    "# Частоты символов\nfreq = {}\nfor ch in 'abracadabra':\n    freq[ch] = freq.get(ch, 0) + 1\nprint(freq)",
    "# Количество информации\nN = 256\nbits = N.bit_length()\nprint(bits)  # 9 бит",
    "# Сдвиг массива\na = [1, 2, 3, 4]\nx = a.pop(0)\na.append(x)\nprint(a)  # [2, 3, 4, 1]",
    "# Пары по условию\npairs = 0\nfor x in range(1, 51):\n    for y in range(1, 51):\n        if x + y == 50 and x < y:\n            pairs += 1\nprint(pairs)",
    "# Обратный цикл\nfor n in range(10, 0, -1):\n    print(n, end=' ')\n# 10 9 8 ... 1"
];

function initCodeBackground() {
    var bg = document.getElementById('codeBg');
    if (!bg) return;

    // очищаем старые колонки — иначе при ресайзе они накладываются друг на друга
    bg.innerHTML = '';

    var w = window.innerWidth;
    // на мобильных — 1 тонкая колонка, на планшетах — 2, на десктопе 3-8
    var cols = w < 480 ? 1 : (w < 768 ? 2 : Math.min(8, Math.floor(w / 220)));
    for (var i = 0; i < cols; i++) {
        var col = document.createElement('div');
        col.className = 'code-col ' + (i % 2 === 0 ? 'up' : 'down');
        col.style.left = (i * (100 / cols)).toFixed(2) + '%';
        col.style.width = (100 / cols).toFixed(2) + '%';

        var parts = [];
        for (var k = 0; k < 9; k++) {
            parts.push(CODE_SNIPPETS[(i * 5 + k * 3) % CODE_SNIPPETS.length]);
        }
        var text = parts.join('\n');

        // два одинаковых блока для бесшовной прокрутки
        var block1 = document.createElement('div');
        block1.className = 'code-col-inner';
        block1.textContent = text;
        var block2 = document.createElement('div');
        block2.className = 'code-col-inner';
        block2.textContent = text;

        col.appendChild(block1);
        col.appendChild(block2);

        col.style.animationDuration = (22 + i * 5) + 's';
        col.style.animationDelay = '-' + (i * 2.6) + 's';
        bg.appendChild(col);
    }
}

// пересоздаём фон при ресайзе (с debounce, чтобы не тормозить)
var _codeBgTimer = null;
window.addEventListener('resize', function() {
    if (_codeBgTimer) clearTimeout(_codeBgTimer);
    _codeBgTimer = setTimeout(function() { initCodeBackground(); }, 250);
});
// ---- Редактор кода: подсветка под язык + нумерация строк ----
(function() {
    'use strict';

    var KEYWORDS = new Set(('def class return if elif else for while import from as try ' +
        'except finally with in not and or is None True False pass break continue ' +
        'lambda global nonlocal raise yield del assert async await print').split(' '));

    // ключевые слова C-подобных языков (JS, TS, Java, C++, C#, Go, Rust, PHP)
    var KEYWORDS_CLIKE = new Set((
        'if else for while do switch case default break continue return ' +
        'function class new this super extends implements interface static ' +
        'public private protected final void int double float long short byte ' +
        'boolean char string bool var let const typeof instanceof delete in of ' +
        'try catch finally throw throws import export from as async await ' +
        'yield null undefined true false None False True self ' +
        'package func defer go chan map struct type range select ' +
        'fn mut pub impl match enum use mod crate trait ref move where ' +
        'unsafe loop dyn box extern const unsigned signed namespace using ' +
        'override abstract virtual template echo foreach require ' +
        'make len append println printf cout cin endl str vec fmt').split(' '));

    function escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    // Общий движок подсветки. cfg:
    //   hash: 'comment' (Python, PHP) | 'directive' (C/C#) | null
    //   lineComment, blockComment, tripleQuotes, templateString — флаги синтаксиса
    //   keywords — набор ключевых слов, caseInsensitiveKw — без учёта регистра
    function highlightWith(code, cfg) {
        var groups = [];
        if (cfg.hash) {
            groups.push(['#[^\\n]*', cfg.hash === 'comment' ? 'tok-c' : 'tok-m']);
        }
        if (cfg.lineComment) groups.push(['\\/\\/[^\\n]*', 'tok-c']);
        if (cfg.blockComment) groups.push(['\\/\\*[\\s\\S]*?\\*\\/', 'tok-c']);
        if (cfg.tripleQuotes) {
            groups.push(['"""[\\s\\S]*?"""|\'\'\'[\\s\\S]*?\'\'\'', 'tok-s']);
        }
        if (cfg.templateString) groups.push(['`(?:[^`\\\\]|\\\\.)*`', 'tok-s']);
        groups.push(['"(?:[^"\\\\\\n]|\\\\.)*"|\'(?:[^\'\\\\\\n]|\\\\.)*\'', 'tok-s']);
        groups.push(['\\b\\d+(?:\\.\\d+)?[jJfFlLuU]?\\b', 'tok-n']);
        groups.push(['[A-Za-z_][A-Za-z0-9_]*', 'ID']);

        var pattern = groups.map(function(g) {
            return '(' + g[0] + ')';
        }).join('|');
        var re = new RegExp(pattern, 'g');
        var out = '', last = 0, m;
        while ((m = re.exec(code)) !== null) {
            if (m.index > last) out += escapeHtml(code.slice(last, m.index));
            var text = null, cls = null;
            for (var g = 0; g < groups.length; g++) {
                if (m[g + 1] === undefined) continue;
                text = m[g + 1];
                cls = groups[g][1];
                break;
            }
            if (text === null) {
                text = m[0];
                cls = 'tok-b';
            } else if (cls === 'ID') {
                // идентификатор: ключевое слово, вызов функции или просто имя
                var rest = code.slice(re.lastIndex).replace(/^\s*/, '');
                var probe = cfg.caseInsensitiveKw ? text.toLowerCase() : text;
                if (cfg.keywords.has(probe)) cls = 'tok-k';
                else if (rest.charAt(0) === '(') cls = 'tok-f';
                else cls = 'tok-b';
            }
            out += '<span class="' + cls + '">' + escapeHtml(text) + '</span>';
            last = re.lastIndex;
        }
        if (last < code.length) out += escapeHtml(code.slice(last));
        return out;
    }

    // ключевые слова SQL: пишем в верхнем регистре, но подсветка
    // не должна зависеть от того, как набрал ученик
    var KEYWORDS_SQL = new Set(('select from where and or not in between like '
        + 'is null as join left right inner outer on group by having order '
        + 'asc desc limit offset insert into values update set delete create '
        + 'table primary key foreign references default distinct union all '
        + 'count sum avg min max case when then else end exists').split(' '));

    var HIGHLIGHTERS = {
        python: function(code) {
            return highlightWith(code, {hash: 'comment', tripleQuotes: true,
                                        keywords: KEYWORDS});
        },
        javascript: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        templateString: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        typescript: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        templateString: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        java: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        cpp: function(code) {
            return highlightWith(code, {hash: 'directive', lineComment: true,
                                        blockComment: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        csharp: function(code) {
            return highlightWith(code, {hash: 'directive', lineComment: true,
                                        blockComment: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        go: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        templateString: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        rust: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        keywords: KEYWORDS_CLIKE});
        },
        php: function(code) {
            return highlightWith(code, {hash: 'comment', lineComment: true,
                                        blockComment: true,
                                        keywords: KEYWORDS_CLIKE,
                                        caseInsensitiveKw: true});
        },
        sql: function(code) {
            return highlightWith(code, {lineComment: true, blockComment: true,
                                        keywords: KEYWORDS_SQL,
                                        caseInsensitiveKw: true});
        }
    };

    function makeHighlighter(lang) {
        return HIGHLIGHTERS[lang] || HIGHLIGHTERS.python;
    }

    function parseMaxHeight(el) {
        // вытащить max-height из computedStyle (поддерживает '45vh', '320px', 'none')
        var cs = getComputedStyle(el);
        var mh = cs.maxHeight;
        if (!mh || mh === 'none') return 0;
        if (mh.indexOf('vh') !== -1) return parseFloat(mh) * window.innerHeight / 100;
        if (mh.indexOf('px') !== -1) return parseFloat(mh);
        return parseFloat(mh) || 0;
    }

    // Универсальный редактор: подсветка задаётся функцией highlightFn
    function initEditor(root, highlightFn) {
        var input = root.querySelector('.pe-input');
        var gutter = root.querySelector('.pe-gutter');
        var hl = root.querySelector('.pe-highlight');
        var body = root.querySelector('.pe-body');
        if (!input || !gutter || !hl || !body) return;

        // максимальная вместимость редактора (атрибут data-min-lines на .pyeditor;
        // по умолчанию 500 — песочница; в уроках хватит 30)
        var minLines = parseInt(root.getAttribute('data-min-lines'), 10);
        if (!minLines || isNaN(minLines) || minLines < 1) minLines = 500;

        function render() {
            hl.innerHTML = highlightFn(input.value);
            var count = (input.value.match(/\n/g) || []).length + 1;

            var cs = getComputedStyle(input);
            var lineH = parseFloat(cs.lineHeight);
            if (!lineH || isNaN(lineH)) lineH = parseFloat(cs.fontSize) * 1.7;

            // сколько строк помещается в видимой области — чтобы внизу
            // всегда был запас для прокрутки и номера не обрывались
            var visLines = 4;
            var bodyH = body.getBoundingClientRect().height;
            if (bodyH > 0) {
                visLines = Math.max(4, Math.ceil(bodyH / lineH));
            } else {
                // на мобильных height:auto → читаем max-height из CSS
                var maxH = parseMaxHeight(body);
                if (maxH) visLines = Math.max(3, Math.floor(maxH / lineH));
            }
            // на мобильных не растягиваем редактор — только по коду
            if (window.innerWidth <= 768) {
                visLines = count;
            }
            // номера строк = фактический код + небольшой запас вниз,
            // но минимум — вся видимая область (строки «добавляются сами»)
            var total = Math.max(count + 1, visLines);

            var nums = '';
            for (var i = 1; i <= total; i++) nums += i + '\n';
            gutter.textContent = nums;

            syncScroll();
        }
        // Подсветка лежит в потоке и сама задаёт размеры области, а
        // прозрачная textarea накрывает её сверху. Обе части всегда
        // совпадают по высоте, прокручивает только контейнер .pe-body.
        // Раньше textarea скроллилась сама плюс контейнер — строки
        // наезжали друг на друга, а номера не совпадали с кодом.
        function syncScroll() {
            var h = hl.offsetHeight;
            if (h > 0) {
                input.style.height = h + 'px';
                input.style.minHeight = h + 'px';
            }
        }
        input.addEventListener('input', render);
        window.addEventListener('resize', render);
        render();
    }

    function initPyEditor(root) { initEditor(root, HIGHLIGHTERS.python); }
    function initJsEditor(root) { initEditor(root, HIGHLIGHTERS.javascript); }
    function initJavaEditor(root) { initEditor(root, HIGHLIGHTERS.java); }
    function initCppEditor(root) { initEditor(root, HIGHLIGHTERS.cpp); }

    // подсветка доступна и другим скриптам страницы
    window.CodigoHighlighters = HIGHLIGHTERS;

    // редактор с явным языком в разметке: data-codeeditor="rust"
    function initCodeEditor(root) {
        var lang = root.getAttribute('data-codeeditor') || 'python';
        initEditor(root, makeHighlighter(lang));
    }

    document.addEventListener('DOMContentLoaded', function() {
        var byAttr = [
            ['[data-pyeditor]', initPyEditor],
            ['[data-jseditor]', initJsEditor],
            ['[data-javaeditor]', initJavaEditor],
            ['[data-cppeditor]', initCppEditor],
            ['[data-codeeditor]', initCodeEditor]
        ];
        for (var a = 0; a < byAttr.length; a++) {
            var nodes = document.querySelectorAll(byAttr[a][0]);
            for (var i = 0; i < nodes.length; i++) {
                byAttr[a][1](nodes[i]);
            }
        }
    });
})();
// ============================================================
//  Звуки кликов + фоновая релакс-музыка (Web Audio, без файлов)
//  ============================================================
(function() {
    'use strict';

    var ctx = null;
    var master = null;
    var musicGain = null;
    var musicOn = localStorage.getItem('codigo_music') !== 'off';
    var soundsOn = localStorage.getItem('codigo_sounds') !== 'off';
    var musicNodes = [];
    var schedulerTimer = null;
    var nextChordTime = 0;
    var chordIndex = 0;

    // мягкие аккорды-пады для фона: Cmaj7, Am7, Fmaj7, Gmaj7, Dmaj7, Em7
    var CHORDS = [
        [261.63, 329.63, 392.00, 493.88],
        [220.00, 261.63, 329.63, 392.00],
        [174.61, 220.00, 261.63, 329.63],
        [196.00, 246.94, 293.66, 392.00],
        [246.94, 293.66, 369.99, 440.00],
        [164.81, 196.00, 246.94, 329.63]
    ];

    function ensureCtx() {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return false;
        if (!ctx) {
            ctx = new AC();
            master = ctx.createGain();
            master.gain.value = 0.9;
            master.connect(ctx.destination);
            musicGain = ctx.createGain();
            musicGain.gain.value = musicOn ? 0.13 : 0.0001;
            musicGain.connect(master);
        }
        if (ctx.state === 'suspended') ctx.resume();
        return true;
    }

    // короткий мягкий «пик» при клике; тип меняет высоту тона
    function playClick(type) {
        if (!soundsOn || !ensureCtx()) return;
        try {
            var t = ctx.currentTime;
            var freq;
            if (type === 'primary') freq = 880;
            else if (type === 'danger') freq = 520;
            else if (type === 'success') freq = 660;
            else freq = 740;

            var o = ctx.createOscillator();
            var g = ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(freq, t);
            o.frequency.exponentialRampToValueAtTime(freq * 0.75, t + 0.1);
            g.gain.setValueAtTime(0.001, t);
            g.gain.exponentialRampToValueAtTime(type === 'ghost' ? 0.04 : 0.06, t + 0.01);
            g.gain.exponentialRampToValueAtTime(0.0001, t + 0.13);
            o.connect(g);
            g.connect(master);
            o.start(t);
            o.stop(t + 0.15);
        } catch (e) { /* звук некритичен */ }
    }
// одна «нота» пада: два осциллятора + фильтр, медленное плавное начало
    function buildVoice(t, freq, det, wave, vol, dur) {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        var f = ctx.createBiquadFilter();
        o.type = wave;
        o.frequency.setValueAtTime(freq * det, t);
        f.type = 'lowpass';
        f.frequency.setValueAtTime(900, t);
        f.Q.setValueAtTime(0.7, t);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(vol, t + 2.2);
        g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
        o.connect(g);
        g.connect(f);
        f.connect(musicGain);
        o.onended = function() {
            try { g.disconnect(); } catch (e2) {}
            try { f.disconnect(); } catch (e2) {}
            var idx = musicNodes.indexOf(o);
            if (idx > -1) musicNodes.splice(idx, 1);
        };
        o.start(t);
        o.stop(t + dur + 0.5);
        return o;
    }

    function scheduleChord() {
        if (!musicOn || !ctx) return;
        var t = Math.max(nextChordTime, ctx.currentTime + 0.02);
        var chord = CHORDS[chordIndex % CHORDS.length];
        chordIndex++;
        var dur = 7.5;

        for (var i = 0; i < chord.length; i++) {
            var freq = chord[i];
            musicNodes.push(buildVoice(t, freq, 1.0, 'sine', 0.045, dur));
            musicNodes.push(buildVoice(t, freq, 1.003, 'triangle', 0.026, dur));
        }

        nextChordTime = t + dur - 0.6;
        schedulerTimer = setTimeout(scheduleChord,
            Math.max(50, (nextChordTime - ctx.currentTime) * 1000));
    }

    function startMusic() {
        if (!musicOn || !ensureCtx()) return;
        if (schedulerTimer) return;
        nextChordTime = ctx.currentTime + 0.15;
        scheduleChord();
    }

    function stopMusic() {
        if (schedulerTimer) {
            clearTimeout(schedulerTimer);
            schedulerTimer = null;
        }
        var t = ctx ? ctx.currentTime : 0;
        if (ctx && musicGain) {
            musicGain.gain.cancelScheduledValues(t);
            musicGain.gain.setValueAtTime(Math.max(musicGain.gain.value || 0.13, 0.0001), t);
            musicGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.6);
        }
        var nodes = musicNodes.slice();
        musicNodes = [];
        nodes.forEach(function(n) {
            try { n.stop(t + 0.1); } catch (e2) {}
            try { n.disconnect(); } catch (e2) {}
        });
    }

    function toggleMusic() {
        if (!ensureCtx()) return;
        musicOn = !musicOn;
        localStorage.setItem('codigo_music', musicOn ? 'on' : 'off');
        var t = ctx.currentTime;
        if (musicOn) {
            musicGain.gain.cancelScheduledValues(t);
            musicGain.gain.setValueAtTime(0.0001, t);
            musicGain.gain.exponentialRampToValueAtTime(0.13, t + 1.2);
            startMusic();
            playClick('success');
        } else {
            stopMusic();
            playClick('default');
        }
        updateMusicBtn();
    }

    function toggleSounds() {
        soundsOn = !soundsOn;
        localStorage.setItem('codigo_sounds', soundsOn ? 'on' : 'off');
        if (soundsOn) playClick('success');
        updateSoundsBtn();
    }
function updateMusicBtn() {
        var b = document.getElementById('musicBtn');
        if (!b) return;
        var icon = b.querySelector('i');
        if (!icon) return;
        if (musicOn) {
            icon.className = 'bi bi-music-note-beamed';
            b.title = 'Выключить фоновую музыку';
            b.classList.remove('off');
            b.classList.add('on');
        } else {
            icon.className = 'bi bi-volume-mute-fill';
            b.title = 'Включить фоновую музыку';
            b.classList.remove('on');
            b.classList.add('off');
        }
    }

    function updateSoundsBtn() {
        var b = document.getElementById('soundsBtn');
        if (!b) return;
        var icon = b.querySelector('i');
        if (!icon) return;
        if (soundsOn) {
            icon.className = 'bi bi-volume-up';
            b.title = 'Выключить звуки кликов';
            b.classList.remove('off');
        } else {
            icon.className = 'bi bi-volume-mute-fill';
            b.title = 'Включить звуки кликов';
            b.classList.add('off');
        }
    }

    // первый клик/клавиша разблокирует аудио (этого требует браузер)
    function firstInteraction() {
        if (ensureCtx() && musicOn) startMusic();
        document.removeEventListener('pointerdown', firstInteraction);
        document.removeEventListener('keydown', firstInteraction);
    }
    document.addEventListener('pointerdown', firstInteraction);
    document.addEventListener('keydown', firstInteraction);

    // звук при клике по кнопкам и ссылкам
    document.addEventListener('click', function(ev) {
        var el = ev.target && ev.target.closest ?
            ev.target.closest('a, button, .btn, .nav-link, .navbar-toggler, .btn-close, input[type=submit]') : null;
        if (!el) return;
        if (el.closest('#soundDock')) return; // кнопки дока играют свои звуки
        if (!soundsOn) return;
        var cls = el.className || '';
        var type = 'default';
        if (/btn-primary/.test(cls) || /btn-xl/.test(cls) || el.classList.contains('navbar-toggler')) {
            type = 'primary';
        } else if (/btn-danger/.test(cls) || /btn-close/.test(cls) || /btn-ghost/.test(cls)) {
            type = 'danger';
        } else if (/btn-success/.test(cls)) {
            type = 'success';
        }
        playClick(type);
    });

    document.addEventListener('DOMContentLoaded', function() {
        updateMusicBtn();
        updateSoundsBtn();
        var mb = document.getElementById('musicBtn');
        var sb = document.getElementById('soundsBtn');
        if (mb) mb.addEventListener('click', function(ev) { ev.preventDefault(); toggleMusic(); });
        if (sb) sb.addEventListener('click', function(ev) { ev.preventDefault(); toggleSounds(); });
    });
})();

// Защита запросов от подделки (CSRF).
// Токен берётся из <meta name="csrf-token"> и добавляется ко всем fetch-
// запросам, а к обычным POST-формам — скрытым полем. Без токена сервер
// отклоняет запрос: чужой сайт не сможет отправить форму от твоего имени.
(function() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    var token = meta ? meta.getAttribute('content') : '';
    window.CSRF_TOKEN = token || '';
    if (!token || typeof window.fetch !== 'function') return;

    var originalFetch = window.fetch.bind(window);
    window.fetch = function(input, init) {
        init = init || {};
        var url = (typeof input === 'string')
            ? input
            : ((input && input.url) || '');
        var sameOrigin = url.indexOf('http') !== 0 ||
            url.indexOf(window.location.origin) === 0;
        if (sameOrigin) {
            init.credentials = init.credentials || 'same-origin';
            var headers = new Headers(
                init.headers || (input && input.headers) || {});
            if (!headers.has('X-CSRF-Token')) {
                headers.set('X-CSRF-Token', token);
            }
            init.headers = headers;
        }
        return originalFetch(input, init);
    };

    document.addEventListener('submit', function(event) {
        var form = event.target;
        if (!form || form.tagName !== 'FORM') return;
        if ((form.getAttribute('method') || 'get').toLowerCase() !== 'post') return;
        if (form.querySelector('input[name="csrf_token"]')) return;
        var field = document.createElement('input');
        field.type = 'hidden';
        field.name = 'csrf_token';
        field.value = token;
        form.appendChild(field);
    }, true);
})();

