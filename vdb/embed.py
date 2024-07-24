# -*- coding: utf-8 -*-

import base64
import json
import http.client

import sys, os

#상위폴더 secret_key 찾기
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import secret_key

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/api-tools/embedding/v2/89dbe6c9157c41fabdbd4e7fd2275e4e', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['embedding']
        else:
            return 'Error'

def embedding(input_text):

    completion_executor = CompletionExecutor(
        host='clovastudio.apigw.ntruss.com',
        api_key=secret_key.API_KEY,
        api_key_primary_val = secret_key.API_KEY_PRIMAL_VAL,
        request_id='402fcd79-7e07-4dd2-844b-6e4c093392f9'
    )
    
    request_data = { "text" : input_text }
    # request_data = json.loads({ "text" : input_text }, strict=False)
    # print(request_data)
    response_text = completion_executor.execute(request_data)
    #print(len(response_text))
    return response_text

if __name__ == '__main__':
    embedding("한국어 문장과 작법 1234")