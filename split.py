#!/usr/bin/env python3

from subprocess import call
import sys

import google_tts

testfile = sys.argv[1]
fp = open(testfile, 'r')

content = fp.read()
print(len(content))
paragraphs = content.split('\n\n')
print(len(paragraphs))
subtotal = 0
parts = []
buffer = ''
for p in paragraphs:
    if subtotal + len(p) <= 4500:
        pass
    else:
        parts.append(buffer)
        buffer = ''
    buffer += p + '\n\n'
    subtotal = len(buffer)
parts.append(buffer)
print(len(parts))

counter = 0
file_list = []
for p in parts:
    counter += 1
    print(p)
    mp3_file = '{}.mp3'.format(counter)
    google_tts.synthesize_text(p, mp3_file)
    file_list.append(mp3_file)

fp.close()

# concatenate files
cmd = 'ffmpeg -i "{}" -acodec copy "{}"'.format(
    'concat:{}'.format('|'.join(file_list)),
    testfile + '.mp3',
)
call(cmd, shell=True)
