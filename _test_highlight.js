// Тест подсветки всех языков: загружаем static/script.js с заглушками DOM
const fs = require('fs');

const el = () => ({
    addEventListener() {}, appendChild() {}, classList: {add() {}, remove() {}},
    style: {}, querySelector: () => null, querySelectorAll: () => [],
    getBoundingClientRect: () => ({height: 0}), textContent: '', innerHTML: '',
    setAttribute() {}, getAttribute: () => null
});

global.document = {
    addEventListener() {}, querySelector: () => null, querySelectorAll: () => [],
    createElement: el, body: el(), documentElement: el(), head: el()
};
global.window = {
    addEventListener() {}, innerWidth: 1200, innerHeight: 800,
    matchMedia: () => ({matches: false, addEventListener() {}})
};
global.getComputedStyle = () => ({
    maxHeight: 'none', lineHeight: '20px', fontSize: '14px',
    paddingTop: '0px', paddingBottom: '0px'
});
global.AudioContext = function() { return {createGain: () => ({connect() {}, gain: {}})}; };

const src = fs.readFileSync('static/script.js', 'utf8');
const store = {
    _d: {}, getItem(k) { return k in this._d ? this._d[k] : null; },
    setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; }
};
const sandbox = {document: global.document, window: global.window,
                 getComputedStyle: global.getComputedStyle, console,
                 localStorage: store, sessionStorage: store,
                 requestAnimationFrame: (f) => setTimeout(f, 0),
                 setTimeout, clearTimeout, setInterval, clearInterval};
const vm = require('vm');
vm.createContext(sandbox);
vm.runInContext('window.CodigoHighlighters = undefined;', sandbox);
vm.runInContext(src, sandbox);

const H = sandbox.window.CodigoHighlighters;
if (!H) {
    console.log('ПРОБЛЕМА: window.CodigoHighlighters не определён');
    process.exit(1);
}

const samples = {
    python: 'def f(x):\n    # коммент\n    s = "строка"\n    return x + 1  # число 42\n',
    javascript: '// коммент\nconst f = (x) => { return `t${x}` + "s"; };\nconst n = 42;\n',
    typescript: 'interface U { name: string }\nconst u: U = {name: "A"};\nconsole.log(u);\n',
    java: 'public class Main {\n  public static void main(String[] a) {\n    int x = 10; // коммент\n    System.out.println("hi" + x);\n  }\n}\n',
    cpp: '#include <iostream>\nint main() {\n  std::cout << "hi" << 10 << std::endl; // c\n  return 0;\n}\n',
    csharp: 'using System;\nclass P {\n  static void Main() { Console.WriteLine($"x {5}"); }\n}\n',
    go: 'package main\n\nfunc main() {\n  x := 1 // c\n  fmt.Println("hi", x)\n}\n',
    rust: 'fn main() {\n  let name = "A"; // c\n  println!("{}", name);\n}\n',
    php: '<?php // c\n$n = 10;\necho "hi $n";\n'
};

let bad = 0;
for (const [lang, code] of Object.entries(samples)) {
    const fn = H[lang];
    if (!fn) { console.log('НЕТ подсветки для', lang); bad++; continue; }
    const html = fn(code);
    const unescaped = html.replace(/<span class="tok-[a-z]+">/g, '')
                          .replace(/<\/span>/g, '');
    const decoded = unescaped.replace(/&lt;/g, '<').replace(/&gt;/g, '>')
                             .replace(/&amp;/g, '&');
    const ok = decoded === code;
    const kw = (html.match(/tok-k/g) || []).length;
    const str = (html.match(/tok-s/g) || []).length;
    const com = (html.match(/tok-c/g) || []).length;
    const num = (html.match(/tok-n/g) || []).length;
    if (!ok) bad++;
    console.log(`${ok ? 'OK ' : 'FAIL'} ${lang.padEnd(11)} kw=${kw} str=${str} com=${com} num=${num}`);
    if (!ok) {
        console.log('   вход :', JSON.stringify(code));
        console.log('   выход:', JSON.stringify(decoded));
    }
}
console.log(bad === 0 ? 'ВСЕ ЯЗЫКИ: подсветка не теряет и не искажает код'
                      : 'ПРОБЛЕМ: ' + bad);

// --- инициализация редактора на странице: DOMContentLoaded -> initEditor ---
console.log('\n[2] Инициализация редактора по data-codeeditor');
const sample = 'fn main() {\n  let x = 1; // ok\n  println!("hi", x);\n}\n';
const editorLang = 'rust';

function makeNode() {
    const handlers = {};
    return {
        textContent: '', innerHTML: '', value: '', scrollLeft: 0,
        offsetHeight: 20, style: {},
        addEventListener(ev, fn) { handlers[ev] = fn; },
        _fire(ev) { if (handlers[ev]) handlers[ev]({}); },
        querySelectorAll: () => [],
        querySelector: () => makeNode(),
        getAttribute: () => null,
        getBoundingClientRect: () => ({height: 0}),
        _handlers: handlers
    };
}

const input = makeNode();
const gutter = makeNode();
const hl = makeNode();
const body = makeNode();
body.getBoundingClientRect = () => ({height: 400});

const root = {
    getAttribute: (name) => (name === 'data-codeeditor' ? editorLang : '40'),
    addEventListener() {},
    querySelector: (sel) => ({
        '.pe-input': input, '.pe-gutter': gutter,
        '.pe-highlight': hl, '.pe-body': body
    })[sel] || null
};

const readyFns = [];
const sandbox2 = {
    document: {
        addEventListener(ev, fn) {
            if (ev === 'DOMContentLoaded') readyFns.push(fn);
        },
        querySelector: () => null,
        getElementById: () => null,
        querySelectorAll: (sel) => (sel === '[data-codeeditor]' ? [root] : []),
        createElement: el, body: el(), documentElement: el()
    },
    window: {addEventListener() {}, innerWidth: 1200, innerHeight: 800,
             matchMedia: () => ({matches: false, addEventListener() {}})},
    getComputedStyle: () => ({maxHeight: 'none', lineHeight: '20px',
                             fontSize: '14px', paddingTop: '0px',
                             paddingBottom: '0px'}),
    console, localStorage: store, sessionStorage: store,
    requestAnimationFrame: (f) => setTimeout(f, 0),
    setTimeout, clearTimeout, setInterval, clearInterval
};
vm.createContext(sandbox2);
vm.runInContext(src, sandbox2);
if (!readyFns.length) {
    console.log('ПРОБЛЕМА: DOMContentLoaded обработчик не зарегистрирован');
    process.exit(1);
}
input.value = sample;
readyFns.forEach((fn) => fn());
const hled = hl.innerHTML;
const gut = gutter.textContent.trim().split('\n').length;
const kwOk = hled.includes('tok-k');
const codeKept = hled.replace(/<span class="tok-[a-z]+">/g, '')
                     .replace(/<\/span>/g, '')
                     .replace(/&quot;/g, '"').includes('fn main');
console.log('   подсветка заполнена:', kwOk ? 'да' : 'НЕТ');
console.log('   строк в нумерации:  ', gut);
console.log('   код сохранён:       ', codeKept ? 'да' : 'НЕТ');
if (!kwOk || !codeKept || gut < 5) {
    console.log('ПРОБЛЕМА: редактор не инициализировался');
    process.exit(1);
}
console.log('РЕДАКТОР: инициализация по data-codeeditor работает');
