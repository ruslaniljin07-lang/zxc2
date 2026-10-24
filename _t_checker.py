"""Temp: smoke-test for utils/code_checker.py across all languages."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\rusla\.cline\data\workspaces\chat\zxc2')

from utils.code_checker import check_code, run_sandbox_code  # noqa: E402

CASES = [
    ('python', 'stdout', 'print("Привет, мир!")', 'Привет, мир!'),
    ('javascript', 'stdout_js', 'console.log("Привет, мир!");', 'Привет, мир!'),
    ('typescript', 'stdout_ts',
     'const n: number = 5;\nconsole.log(n + 7);', '12'),
    ('go', 'stdout_go',
     'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println(5 + 7)\n}',
     '12'),
    ('rust', 'stdout_rust',
     'fn main() {\n    println!("{}", 5 + 7);\n}', '12'),
    ('java', 'stdout_java',
     'public class Main {\n    public static void main(String[] args) {\n'
     '        System.out.println(5 + 7);\n    }\n}', '12'),
    ('cpp', 'stdout_cpp',
     '#include <iostream>\nusing namespace std;\n\nint main() {\n'
     '    cout << 5 + 7 << endl;\n    return 0;\n}', '12'),
    ('csharp', 'stdout_csharp',
     'using System;\n\nclass Program {\n    static void Main() {\n'
     '        Console.WriteLine(5 + 7);\n    }\n}', '12'),
    ('php', 'stdout_php', '<?php\necho 5 + 7;', '12'),
]

REQUIRE = {
    'java': ['System.out.println'],
    'cpp': ['cout', 'int main'],
    'csharp': ['Console.WriteLine'],
    'php': ['echo'],
    'rust': ['println!'],
}

for lang, ctype, code, expected in CASES:
    check = {'type': ctype, 'expected': expected}
    req = REQUIRE.get(lang)
    if req:
        check['require'] = req
    res = check_code(code, check)
    print(f'--- {lang} ({ctype}): success={res.get("success")}')
    out = (res.get('stdout') or '').strip()
    err = (res.get('stderr') or '').strip()
    print(f'    stdout={out[:70]!r}')
    if err:
        print(f'    stderr={err[:160]!r}')

# заведомо неверное решение должно падать
bad = check_code('console.log(5);', {'type': 'stdout_js', 'expected': '12'})
print('--- wrong js solution success =', bad.get('success'))

sb = run_sandbox_code('package main\n\nimport "fmt"\n\nfunc main() { fmt.Println(1) }',
                      5, 'go')
print('--- sandbox go:', sb.get('success'), repr((sb.get('stdout') or '').strip()))
sb2 = run_sandbox_code('print(2 + 2)', 5, 'python')
print('--- sandbox python:', sb2.get('success'), repr((sb2.get('stdout') or '').strip()))