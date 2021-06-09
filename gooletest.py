#!/usr/bin/env python

# for credentials see https://cloud.google.com/docs/authentication/getting-started

import sys

import google.cloud

def synthesize_text_file(text_file):
    """Synthesizes speech from the input file of text."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    with open(text_file, "r") as f:
        text = f.read()
        # convert plain text to SSML
        # Wait 1 second on each line break
        ssml = "<speak>{}</speak>".format(
            text.replace("\n\n", '.<break time="1s"/>\n\n')
        )
        input_text = texttospeech.SynthesisInput(ssml=ssml)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        name='en-US-Wavenet-D',
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    output_file = text_file + '.mp3'
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "{}"'.format(output_file))

synthesize_text_file(sys.argv[1])
