path = 'build_courses.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
start = None
for i, line in enumerate(lines):
    if "if __name__ == '__main__':" in line:
        if start is None:
            start = i
        else:
            # second occurrence: cut from here
            del lines[i:]
            break
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('done, lines =', len(lines))