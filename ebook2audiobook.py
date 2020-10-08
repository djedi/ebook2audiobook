#!/usr/bin/python3

import sys 
import glob
import os
from pathlib import Path
from subprocess import call, check_output

try:
    txt_dir = sys.argv[1]
except IndexError:
    print('Usage: pass in directory that contains txt files to convert to audio.')
    exit()

# Look for cover.jpg in txt_dir
cover_filename = os.path.join(txt_dir, 'cover.jpg')
if not os.path.isfile(cover_filename):
    cont = input('cover.jpg is missing, would you like to continue [y/N]? ')
    try:
        if cont[0].lower() != 'y':
            exit()
    except IndexError:
        exit()

title = input('Audiobook Title: ')
author = input('Audiobook Author: ')
txt_dir = sys.argv[1]

file_list_path = os.path.join(txt_dir, 'FILES')
metadata_path = os.path.join(txt_dir, 'METADATA')

print('# Converting txt files to audio:')
for filename in sorted(glob.glob(os.path.join(txt_dir, '*.txt'))):
    aiff_filename = os.path.join(txt_dir, Path(filename).stem + '.aiff')
    if os.path.isfile(aiff_filename) :
        print('"{}" already exists. Skipping.'.format(aiff_filename))
    else:
        cmd = 'say -f "{}" -o "{}"'.format(voice, filename, aiff_filename)
        print('Converting "{}" to audio...'.format(filename))
        call(cmd, shell=True)

# Now convert aiff files to m4a
print('# Converting aiff files to m4a')
for filename in sorted(glob.glob(os.path.join(txt_dir, '*.aiff'))):
    m4a_filename = os.path.join(txt_dir, Path(filename).stem + '.m4a')
    if os.path.isfile(m4a_filename) :
        print('"{}" already exists. Skipping.'.format(m4a_filename))
    else:
        cmd = 'ffmpeg -i "{}" -c:a libfdk_aac -b:a 64k -f mp4 "{}"'.format(filename, m4a_filename)
        print('Converting "{}" to m4a...'.format(filename))
        call(cmd, shell=True)

# Build metadata file
print('# Building metadata file')
fm = open(metadata_path, 'w')
fm.writelines([
    ';FFMETADATA\n', 
    'title={}\n'.format(title),
    'artist={}\n'.format(author),
    'album={}\n'.format(title),
    'genre=Audiobooks\n',    
])
m4a_files = sorted(glob.glob(os.path.join(txt_dir, '*.m4a')))
fl = open(file_list_path, 'w')
start = 0
end = 0
for filename in m4a_files:
    full_filename = os.path.join(os.getcwd(), filename)
    fl.write('file \'{}\'\n'.format(os.path.basename(filename)))
    cmd = 'ffprobe "{}" -show_entries format=duration -v quiet -of csv="p=0"'.format(full_filename)
    end_output = check_output(cmd, shell=True)
    end += int(float(end_output) * 1000)
    fm.writelines([
        '[CHAPTER]\n',
        'TIMEBASE=1/1000\n',
        'START={}\n'.format(start),
        'END={}\n'.format(end),
        'title={}\n'.format(Path(filename).stem),
    ])
    start = end
fl.close()
fm.close()        

# Compiling ebook
print('# Compiling eBook')
audiobook_name = '{} by {}.m4b'.format(title, author)
cmd = 'ffmpeg -f concat -safe 0 -i "{}" -i "{}" -map_metadata 1 -vn -y -acodec copy "{}"'.format(
    file_list_path, metadata_path, audiobook_name)
call(cmd, shell=True)
cmd = 'mp4art -q --add "{}" "{}"'.format(cover_filename, audiobook_name)
call(cmd, shell=True)