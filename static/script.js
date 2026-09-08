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
// ---- Редактор в стиле PyCharm: подсветка Python + нумерация строк ----
(function() {
    var KEYWORDS = new Set(('def class return if elif else for while import from as try ' +
        'except finally with in not and or is None True False pass break continue ' +
        'lambda global nonlocal raise yield del assert async await print').split(' '));

    function escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function highlightPython(code) {
        var tokenRe = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?''')|("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|(\b\d+(?:\.\d+)?[jJ]?\b)|(\b(?:def|class|return|if|elif|else|for|while|import|from|as|try|except|finally|with|in|not|and|or|is|None|True|False|pass|break|continue|lambda|global|nonlocal|raise|yield|del|assert|async|await)\b)|([A-Za-z_][A-Za-z0-9_]*)/g;
        var out = '';
        var last = 0, m;
        while ((m = tokenRe.exec(code)) !== null) {
            if (m.index > last) out += escapeHtml(code.slice(last, m.index));
            if (m[1] !== undefined) out += '<span class="tok-c">' + escapeHtml(m[1]) + '</span>';
            else if (m[2] !== undefined) out += '<span class="tok-s">' + escapeHtml(m[2]) + '</span>';
            else if (m[3] !== undefined) out += '<span class="tok-s">' + escapeHtml(m[3]) + '</span>';
            else if (m[4] !== undefined) out += '<span class="tok-n">' + escapeHtml(m[4]) + '</span>';
            else if (m[5] !== undefined) out += '<span class="tok-k">' + escapeHtml(m[5]) + '</span>';
            else if (m[6] !== undefined) {
                var id = m[6], isCall = false;
                var rest = code.slice(tokenRe.lastIndex).replace(/^\s*/, '');
                if (rest.charAt(0) === '(') isCall = true;
                if (KEYWORDS.has(id)) {
                    out += '<span class="tok-k">' + escapeHtml(id) + '</span>';
                } else if (isCall) {
                    out += '<span class="tok-f">' + escapeHtml(id) + '</span>';
                } else {
                    out += '<span class="tok-b">' + escapeHtml(id) + '</span>';
                }
            }
            last = tokenRe.lastIndex;
        }
        if (last < code.length) out += escapeHtml(code.slice(last));
        return out;
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

    function initPyEditor(root) {
        var input = root.querySelector('.pe-input');
        var gutter = root.querySelector('.pe-gutter');
        var hl = root.querySelector('.pe-highlight');
        var body = root.querySelector('.pe-body');
        if (!input || !gutter || !hl || !body) return;

        // максимальная вместимость редактора (атрибут data-min-lines на .pyeditor;
        // по умолчанию 500 — песочница; в уроках хватит 50)
        var minLines = parseInt(root.getAttribute('data-min-lines'), 10);
        if (!minLines || isNaN(minLines) || minLines < 1) minLines = 500;

        function render() {
            hl.innerHTML = highlightPython(input.value);
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

            // высота textarea = число строк в коде + запас,
            // но не больше максимума вместимости
            var padTop = parseFloat(cs.paddingTop) || 0;
            var padBottom = parseFloat(cs.paddingBottom) || 0;
            var wantH = total * lineH + padTop + padBottom + 4;
            var capH = (minLines + visLines) * lineH + padTop + padBottom;
            var h = Math.min(wantH, capH);
            input.style.height = Math.round(h) + 'px';
            syncScroll();
        }
        // вертикаль скроллит .pe-body (нативно), горизонталь — textarea
        function syncScroll() {
            hl.style.transform = 'translateX(' + (-input.scrollLeft) + 'px)';
            hl.style.height = input.offsetHeight + 'px';
        }
        input.addEventListener('input', render);
        input.addEventListener('scroll', syncScroll);
        window.addEventListener('resize', render);
        render();
    }

    document.addEventListener('DOMContentLoaded', function() {
        var editors = document.querySelectorAll('[data-pyeditor]');
        for (var i = 0; i < editors.length; i++) initPyEditor(editors[i]);
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
