from setuptools import setup

setup(
    name='remotecheck',
    version='4.0',
    description='A check modules for ops.',

    author='mago960806',
    author_emaill='mago960806@hotmail.com',

    platforms='any',
    install_requires=[
        'paramiko==2.4.2',
        'ping3==1.4.1',
        'xlrd==1.2.0',
        'XlsxWriter==1.1.5'
        'python-Levenshtein==0.12.0'
    ],
    packages=['remotecheck']
)