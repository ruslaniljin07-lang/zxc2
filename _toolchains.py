# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, '.')
from utils.code_checker import _run_java_code, _run_cpp_code  # noqa: E402

java_code = ('public class Main { public static void main(String[] args) '
             '{ System.out.println(1); } }')
print('JAVA raw:', _run_java_code(java_code))

cpp_code = '#include <iostream>\nint main() { std::cout << 1; }'
print('CPP raw:', _run_cpp_code(cpp_code))
