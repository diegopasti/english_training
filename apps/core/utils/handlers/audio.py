import os

from pydub import AudioSegment
from pydub.silence import split_on_silence

from main.settings import MEDIA_URL


def split_audio(audio, directory):
    """
    Splits the audio into multiple files, one per phrase

    :param directory: Directory name for new files
    :param audio: Path of the file containing the audio in the full version
    :return: None
    """

    sound = AudioSegment.from_file(audio)
    parts = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS - 16, keep_silence=250)

    count = 1
    audio_parts = []

    for track in parts:
        new_path = os.path.join(directory, f"{count}.mp3")
        track.export(new_path, format="mp3")
        audio_parts.append(new_path)
        count += 1

    return audio_parts


def merge_audios(files: list, directory) -> str:
    """
    Merge tracks files into one file.
    ffmpeg required, download it and added on os environments.

    :param directory: Directory name for new files
    :param files: List of files that will be merged
    :return: Path of the generated file
    """

    audio = AudioSegment.from_mp3(files[0])
    for track in files[1:]:
        audio += AudioSegment.from_mp3(track)

    new_path = os.path.join(directory, "0.mp3")
    audio.export(new_path, format="mp3")
    return new_path
