import os

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence

from transformers import pipeline
from df.enhance import enhance, init_df, load_audio, save_audio


AudioSegment.converter = f"{os.getcwd()}\\ffmpeg.exe"
AudioSegment.ffprobe = f"{os.getcwd()}\\ffprobe.exe"

datafilter, datafilter_state, _ = init_df(log_level="none")
whisper = pipeline("automatic-speech-recognition", f"{os.getcwd()}\\WhisperModel")

temp_wav_file = "temp_audio.wav"


def remove_silence(audio_segment, silence_thresh=-60, min_silence_len=1000, keep_silence=300):
    non_silent_chunks = split_on_silence(
        audio_segment,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )

    combined_non_silent_audio = AudioSegment.empty()
    for chunk in non_silent_chunks:
        combined_non_silent_audio += chunk

    return combined_non_silent_audio


def improve_audio(audio_segment, remove_noise=True, temp_wav_file=temp_wav_file):
    audio = audio_segment.set_channels(1)
    dbfs = audio.dBFS
    silence_thresh = min(-40, dbfs * 2.5 + 30)

    if remove_noise:
        audio = audio.set_frame_rate(48000)
        audio.export(temp_wav_file, format="wav")
        audio, _ = load_audio(temp_wav_file, sr=datafilter_state.sr())
        enhanced = enhance(datafilter, datafilter_state, audio)
        save_audio(temp_wav_file, enhanced, datafilter_state.sr())
        audio = AudioSegment.from_file(temp_wav_file)

        if os.path.exists(temp_wav_file):
            os.remove(temp_wav_file)

    audio = audio.set_frame_rate(16000)
    audio = remove_silence(audio, silence_thresh=silence_thresh)
    audio = normalize(audio)

    return audio


def convert_and_transcribe(input_file, remove_noise=True, temp_wav_file=temp_wav_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio = improve_audio(audio, remove_noise=remove_noise, temp_wav_file=temp_wav_file)
        audio.export(temp_wav_file, format="wav")

        return whisper(temp_wav_file, generate_kwargs={"language": "russian"}, return_timestamps=True)

    finally:
        # Удаляем временный файл
        if os.path.exists(temp_wav_file):
            os.remove(temp_wav_file)


def whisper_to_texts(whisper_result):
    whole_text = whisper_result["text"]

    separated_text = []
    chunks = whisper_result["chunks"]
    for chunk in chunks:
        separated_text.append(chunk['text'].strip())

    return whole_text, separated_text



if __name__ == "__main__":
    test_audio = "test_audio.mp3"
    audio = AudioSegment.from_file(test_audio)
    better_audio = improve_audio(audio) + 10
    better_audio.export("improved_test_audio.mp3", format="mp3")
    print(convert_and_transcribe(test_audio, remove_noise=True))
    print(convert_and_transcribe(test_audio, remove_noise=False))
