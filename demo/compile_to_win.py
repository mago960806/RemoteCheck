import os
import sys
import shutil
import subprocess

try:
    filename = sys.argv[1]
except IndexError:
    print('[!] 请提供一个需要编译的py文件')
    sys.exit(1)

subprocess.call('pyinstaller.exe --distpath=. -F {} -i icon.ico'.format(filename))

# shutil.rmtree('build')
os.remove(filename.split('.')[0] + '.spec')
