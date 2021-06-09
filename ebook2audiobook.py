#!/usr/bin/env python

import sys
import getopt
import glob
import multiprocessing
import os
from pathlib import Path
from subprocess import call, check_output

USAGE = 'Usage: python3 {} [-v <voice> -t <title> -a <author> --clean] <txt_directory>'.format(sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:], "hcCrv:t:a:", ["help", "clean", "clean-only", "recompile", "voice=", "title=", "author="])
except getopt.GetoptError:
    print(USAGE)
    sys.exit(2)

try:
    txt_dir = args[0]
except IndexError:
    print(USAGE)
    exit()
file_list_path = os.path.join(txt_dir, 'FILES')
metadata_path = os.path.join(txt_dir, 'METADATA')
cover_filename = os.path.join(txt_dir, 'cover.jpg')

voice = None
title = None
author = None

# Look for meta.yaml
meta_yaml = os.path.join(txt_dir, 'meta.yaml')
if os.path.isfile(meta_yaml):
    skip = False
    try:
        import yaml
    except ImportError:
        skip = True
        print("In order to use the yaml featured you will need to install pyyaml.\n> pip install -r requirements.txt")
        cont = input('Would you like to continue [y/N]? ')
        try:
            if cont[0].lower() != 'y':
                exit()
        except IndexError:
            exit()
    if not skip:
        with open(meta_yaml, 'r') as stream:
            try:
                ydata = (yaml.safe_load(stream))
                title = ydata.get('title')
                author = ydata.get('author')
                voice = ydata.get('voice')
            except yaml.YAMLError as exc:
                print (exc)

def clean():
    print("Cleaning...")
    for filename in os.listdir(txt_dir):
        ext = os.path.splitext(filename)[1]
        if ext in ('.m4a', '.aiff') or filename in ('FILES', 'METADATA'):
            os.remove(os.path.join(txt_dir, filename))
            print ('DELETED: {}'.format(filename))

# Compiling ebook
def compile_audiobook():
    print('# Compiling eBook')
    audiobook_name = '{} by {}.m4b'.format(title, author)
    cmd = 'ffmpeg -f concat -safe 0 -i "{}" -i "{}" -map_metadata 1 -vn -y -acodec copy "{}"'.format(
        file_list_path, metadata_path, audiobook_name)
    call(cmd, shell=True)
    cmd = 'mp4art -q --add "{}" "{}"'.format(cover_filename, audiobook_name)
    call(cmd, shell=True)

for o, a in opts:
    if o in ('-h', '--help'):
        print (USAGE)
        exit()
    if o in ('-c', '--clean'):
        clean()
    if o in ('-C', '--clean-only'):
        clean()
        exit()
    if o in ('-v', '--voice'):
        voice = a
        print ('Using voice: {}'.format(voice))
    if o in ('-t', '--title'):
        title = a
        print ('Title: {}'.format(title))
    if o in ('-a', '--author'):
        author = a
        print ('Author: {}'.format(author))
    if o in ('-r', '--recompile'):
        compile_audiobook()
        exit()

# Look for cover.jpg in txt_dir
if not os.path.isfile(cover_filename):
    cont = input('cover.jpg is missing, would you like to continue [y/N]? ')
    try:
        if cont[0].lower() != 'y':
            exit()
    except IndexError:
        exit()

if not title:
    title = input('Audiobook Title: ')
if not author:
    author = input('Audiobook Author: ')


def txt_to_aiff(txt_dir, filename):
    aiff_filename = os.path.join(txt_dir, Path(filename).stem + '.aiff')
    if os.path.isfile(aiff_filename):
        print('"{}" already exists. Skipping.'.format(aiff_filename))
    else:
        use_voice = ''
        if voice:
            use_voice = '-v {} '.format(voice)
        cmd = 'say {}-f "{}" -o "{}" >/dev/null 2>&1'.format(use_voice, filename, aiff_filename)
        print('Converting "{}" to audio...'.format(filename))
        call(cmd, shell=True)


print('# Converting txt files to audio:')
# for filename in sorted(glob.glob(os.path.join(txt_dir, '*.txt'))):
    # aiff_filename = os.path.join(txt_dir, Path(filename).stem + '.aiff')
    # if os.path.isfile(aiff_filename):
    #     print('"{}" already exists. Skipping.'.format(aiff_filename))
    # else:
    #     use_voice = ''
    #     if voice:
    #         use_voice = '-v {} '.format(voice)
    #     cmd = 'say {}-f "{}" -o "{}"'.format(use_voice, filename, aiff_filename)
    #     print('Converting "{}" to audio...'.format(filename))
    #     call(cmd, shell=True)
txt_files = sorted(glob.glob(os.path.join(txt_dir, '*.txt')))
with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
    p.map(txt_to_aiff, [(txt_dir, x) for x in txt_files])


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
compile_audiobook()
