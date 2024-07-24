import sys
import requests
import secret_key

def stt(filename):
    client_id = secret_key.CLIENT_ID
    client_secret = secret_key.CLIENT_SECRET
    lang = "Kor" # 언어 코드 ( Kor, Jpn, Eng, Chn )
    url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang
    data = open('output.wav', 'rb')
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(url,  data=data, headers=headers)
    rescode = response.status_code
    if(rescode == 200):
        # print (response.text)
        return response.text
    else:
        print("Error : " + response.text)

import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
from pydub.playback import play

def record(max_times=5, stop_count=120):
    # 녹음 설정
    FORMAT = pyaudio.paInt16  # 16비트 포맷
    CHANNELS = 1              # 모노 채널
    RATE = 44100              # 샘플링 레이트 (44.1kHz)
    CHUNK = 1024              # 버퍼 크기
    RECORD_SECONDS = max_times       # 녹음 시간(초)
    OUTPUT_FILENAME = "output.wav"  # 저장할 파일 이름

    # pyaudio 객체 생성
    audio = pyaudio.PyAudio()

    # 녹음 시작
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    #레코드 효과음
    sound = AudioSegment.from_wav("thick.wav")
    play(sound)
    
    frames = []
    silience_que = []
    
    #대기모드
    print("WAITING...")
    while True:
        data = stream.read(CHUNK)
        # print(np.abs(np.frombuffer(data, dtype=np.int16)).mean())
        record_flag = (np.abs(np.frombuffer(data, dtype=np.int16)).mean() > 200)
        
        if record_flag:
            frames.append(data)
            break

    #레코딩모드
    print("RECORDING...")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        
        silience_flag = (np.abs(np.frombuffer(data, dtype=np.int16)).mean() < 500)

        if not silience_flag:
            silience_que = []
        else:
            silience_que.append(silience_flag)
            # print(silience_que.count(True))
            
            if silience_que.count(True) > stop_count:
                print("Force STOP...")
                break

    print("STOP...", len(frames))

    # 녹음 종료
    stream.stop_stream()
    stream.close()
    audio.terminate()

    if len(frames) > 130: #130 이하는 무음으로 보고 저장하지 않음
        # WAV 파일로 저장
        waveFile = wave.open(OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        print(f"{OUTPUT_FILENAME} 파일로 저장되었습니다.")
        rtn = stt("output.wav")
        return rtn
    else:
        return None
        
# import numpy as np
# import sounddevice as sd

# def is_silent(data, threshold=0.01):
#     return np.max(np.abs(data)) < threshold

# flag_silent = True

# def monitor_audio(duration=3, threshold=0.01, sample_rate=44100):
#     with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
#         sd.sleep(int(duration * 1000))

# def callback(indata, frames, time, status):
#     if is_silent(indata):
#         print("No sound detected")
#     else:
#         print("detected")
#         flag_silent = False
#         return flag_silent

# import time
# import numpy as np

# def check_silence(duration=3, threshold=500):
#     # pyaudio 객체 생성
#     p = pyaudio.PyAudio()
    
#     # 오디오 스트림 생성
#     stream = p.open(format=pyaudio.paInt16,
#                     channels=1,
#                     rate=44100,
#                     input=True,
#                     frames_per_buffer=1024)
    
#     print("Listening...")

#     start_time = time.time()
#     silent = True

#     while time.time() - start_time < duration:
#         data = np.frombuffer(stream.read(1024), dtype=np.int16)
#         if np.abs(data).mean() > threshold:
#             silent = False
#             break

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     return silent

if __name__ == '__main__':
    # rtn = monitor_audio()
    
    record(max_times=30)
    # stt("output.wav")
