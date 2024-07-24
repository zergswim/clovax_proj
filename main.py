# -*- coding: utf-8 -*-

import requests
import json
import urllib.request

from pydub import AudioSegment
from pydub.playback import play

import rag
import stt
import secret_key

class CLOVA_API_TUNNING2:
    def __init__(self): #, host, api_key, api_key_primary_val, request_id):
        self._host = 'https://clovastudio.stream.ntruss.com'
        self._api_key = secret_key.API_KEY
        self._api_key_primary_val = secret_key.API_KEY_PRIMAL_VAL
        self._request_id = 'fa9605ed-a6be-4dda-8dfe-fe3aed4ad044' #HCX-003
        self._app = '/testapp/v1/tasks/ef9vbgvx/chat-completions'
        
        self._preset_text = [{"role":"system","content":""}]

    def execute(self, request_json):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        # with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
        with requests.post(self._host + self._app,
                           headers=headers, json=request_json, stream=True) as r:
            result_flag = False
            for line in r.iter_lines():
                if line:
                    #event:result 만 추출
                    if line.decode("utf-8") == "event:result":
                        result_flag = True
                    elif result_flag:                    
                        # print("=> ", type(line.decode("utf-8")), line.decode("utf-8"))
                        json_string = line.decode("utf-8").replace("data:","")
                        json_data = json.loads(json_string)
                        return json_data['message']['content']
        
    def call(self, questions):
        preset_text = self._preset_text.copy()

        for q in questions:
            content = {"role":"user","content":q}
            preset_text.append(content)

        #마지막 질문에 대한 검색결과만 추가
        # search_result = Search_Google(q)
        # search_result = "지금 시간은 2024-07-11 오후 3:55"

        print("rag_query:", questions[-1])
        ref_content = rag.query(questions[-1], limit=1)
        print("rag_content:", ref_content)
        
        search_content = {"role":"system","content":f"최대한 참조내용를 고려해서 답변을 해줘 ###참조내용:{ref_content}###"}
        preset_text.append(search_content)

        request_json = {
            'messages': preset_text,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': False,
            'seed': 0
        }
        
        return self.execute(request_json)        
                    
#emotion 0 중립, 1 슬픔, 2 기쁨, 3 분노
def speak(text, speed="0", volume="0", pitch="0", voice="nara", emotion="0"):
    client_id = secret_key.CLIENT_ID
    client_secret = secret_key.CLIENT_SECRET
    encText = urllib.parse.quote(text)
    data = f"speaker={voice}&volume={volume}&speed={speed}&pitch={pitch}&format=mp3&text={encText}" #+ encText;
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode==200):
        print(f"{voice} : {text}")
        # 바로 출력
        # mp3_fp = io.BytesIO(response.read())
        # mp3_fp.seek(0)

        # # pydub를 사용하여 BytesIO에서 음성 데이터를 로드하고 재생
        # audio = AudioSegment.from_file(mp3_fp, format="mp3")
        # play(audio) 

        # 파일로 저장후 출력
        response_body = response.read()
        with open('output.mp3', 'wb') as f:
            f.write(response_body)
        audio = AudioSegment.from_file('output.mp3', format="mp3")
        play(audio) 

    else:
        print("Error Code:" + rescode)                  

def check_emotion(text):
    client_id = secret_key.CLIENT_ID
    client_secret = secret_key.CLIENT_SECRET
    # encText = urllib.parse.quote(text)
    json_text = {"content": text} #encText}
    url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
    
    headers = {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
        'Content-Type': 'application/json; charset=utf-8'
    }

    with requests.post(url, headers=headers, json=json_text, stream=True) as r:
        result_flag = False
        for line in r.iter_lines():
            if line:
                json_string = line.decode("utf-8")#.replace("data:","")
                # print(json_string)
                json_data = json.loads(json_string)
                return json_data['document']['sentiment']  

if __name__ == '__main__':

    question_que = []
    
    # clova_api = CLOVA_API() #베이스모델, 대화큐 필요
    clova_api = CLOVA_API_TUNNING2() #튜닝모델, 대화큐 필요
    # clova_api2 = CLOVA_API_TUNNING() #구)튜닝모델, 대화큐 X
    
    #stt
    while True:    
        rtn = stt.record(max_times=30)
        # print(rtn)
        # rtn = clova_speach_test.stt("output.wav")
        
        if rtn != None:
            rtn_json = json.loads(rtn)
            question = rtn_json['text']
            print("Q:", question)

            if question != "":
                
                #기본 플레이그라운드(대화큐 필요)
                question_que.append(question)
                answer = clova_api.call(question_que)

                #케어콜 테스트(대화큐 필요없음)
                # answer = clova_api.call(question)
                # answer = clova_api.call('어르신:'+question)

                #tts
                if answer != None:
                    # 답변 감정분석 시도하였으나 잘 작동하지 않음..
                    emotion = check_emotion(answer)
                    print(emotion)
                    if emotion == "neutral": em_code = 0
                    if emotion == "positive": em_code = 2
                    if emotion == "negative": em_code = 1
                    #emotion 0 중립, 1 슬픔, 2 기쁨, 3 분노
                    speak(answer, emotion=em_code, speed=-1)