import json
import requests
from time import sleep
import os
import logging
import streamlit as st
import azure.cognitiveservices.speech as speechsdk

try:
    import customvoice
except ImportError:
    print(
        "Please copy folder https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/samples/custom-voice/python/customvoice and keep the same folder structure as github."
    )
    quit()


def speech_synthesis_to_wave_file(
    text: str, output_file_path: str, speaker_profile_id: str, targetlang: str
):
    config = customvoice.Config(key=apikey, region=region, logger=logger)
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(
        subscription=config.key, region=config.region
    )
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
    )
    file_config = speechsdk.audio.AudioOutputConfig(filename=output_file_path)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config
    )

    # use PhoenixLatestNeural if you want word boundary event.  We will support events on DragonLatestNeural in the future.
    ssml = (
        "<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' "
        "xmlns:mstts='http://www.w3.org/2001/mstts'>"
        "<voice name='DragonLatestNeural'>"
        f"<mstts:ttsembedding speakerProfileId='{speaker_profile_id}'/>"
        "<mstts:express-as style='Prompt'>"
        f"<lang xml:lang='{targetlang}'> {text} </lang>"
        "</mstts:express-as>"
        "</voice></speak> "
    )

    print(ssml)

    def word_boundary(evt):
        print(
            f"Word Boundary: Text='{evt.text}', Audio offset={evt.audio_offset / 10000}ms, Duration={evt.duration / 10000}ms, text={evt.text}"
        )

    # speech_synthesizer.synthesis_word_boundary.connect(word_boundary)
    result = speech_synthesizer.speak_ssml_async(ssml).get()

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(
            "Speech synthesized for text [{}], and the audio was saved to [{}]".format(
                text, output_file_path
            )
        )
        print("result id: {}".format(result.result_id))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("result id: {}".format(result.result_id))


logging.basicConfig(
    filename="customvoice.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

apikey = st.sidebar.text_input("Enter your API key", type="password")
speakerProfileId = st.sidebar.text_input("Enter your speaker profile ID")
modelName = st.sidebar.selectbox(
    "Select your base model name", ("DragonLatestNeural", "PhoenixLatestNeural")
)

region = st.sidebar.selectbox(
    "Select your API Region", ("eastus", "westeurope", "southeastasia")
)

targetlang = st.sidebar.selectbox(
    "Select your target language",
    (
        "ja-JP",
        "de-DE",
        "en-US",
        "en-GB",
        "es-ES",
        "fr-FR",
        "it-IT",
        "ko-KR",
        "pt-BR",
        "zh-CN",
    ),
)

text = st.text_input("Enter your text to synthesize")
if st.button("Synthesize"):
    output_file_path = "./output/output.wav"
    speech_synthesis_to_wave_file(
        text=text,
        output_file_path=output_file_path,
        targetlang=targetlang,
        speaker_profile_id=speakerProfileId,
    )
    st.audio(output_file_path, format="audio/wav")
