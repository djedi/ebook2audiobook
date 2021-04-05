# ebook2audiobook

This is basically a script that automates a number of commands to create a text version of an eBook to an Audiobook.

## How to run

Create a directory full of chaptered text files. Chaptered text files such as `Chapter 01.txt`, `Chapter 02.txt`, etc.

Create a cover image and name it `cover.jpg` and put it in the directory with the text files.

Be sure to have [FFmpeg](https://ffmpeg.org/) and [mp4v2](https://github.com/TechSmith/mp4v2) installed. You can install with brew.

```bash
brew install ffmpeg mp4v2
```

Run the script passing in the directory with your files:

```bash
./ebook2audiobook.py "Alice in Wonderland"
```

You can pass the following args into the script:

	-h, --help: Show a short usage snippet
	-c, --clean: clean out old .aiff, .m4a, METADATA, and FILES files before creating audiobook
	-C, --clean-only: clean out old files and exit
	-t, --title: audobook title. If not specified, it will look in the meta.yaml or prompt for it
	-a, --author: audiobook author. If not specified, it will look in the meta.yaml or prompt for it
	-v, --voice: Specify the voice to use in the mac `say` command. If not specified, it will use your default.

You can also save time when testing by creating a `meta.yaml` file to specify the title, author, and voice. Here is an example:

```yaml
Title: Alice’s Adventures in Wonderland
Author: Lewis Carroll
Voice: Samantha
```

I've included a directory named `Alice in Wonderland` so that you can test this script and use it for an example.

You will be prompted for the title and author of the book.

The script will then convert each text file to an audio file, then concatenate them all into on chaptered m4b file.

## Helpful Tips

- Note that chapter files will be compiled in alphabetical order and chapter bookmarks will be named after the file name. So if you have named chapters such as `Introduction`, `Prologue`, etc., then you will need to prefix these with numbers like `00 Introduction`, `01 Prologue`, etc.
- Remove any characters you don't want the text to speak. For example, one book I converted used a lot of underscores to separate ideas. After conversion, the audiobook would sometimes say "underscore, underscore, underscore, underscore, underscore, underscore, underscore, underscore."
- You can set you default voice in System Preferences -> Accessibility -> Speech. Not all voices are supported by `say` - mainly the Siri voices. Or, you could edit the script to pass in a voice using the `-v` options in `say`. Run `say -v ?` to see voice options.

## Contributing

I got this script to a point where it works for what I wanted to do, but it could definitely use some improvements and added error handling, so feel free to submit PRs with useful features.
