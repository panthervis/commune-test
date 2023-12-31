import http.client
import json
import commune as c
import base64

from PIL import Image
from io import BytesIO



class BitAPAI(c.Module):
    
    whitelist = ['forward', 'chat', 'ask', 'generate', 'imagine']

    def __init__(self, api_key:str = None, host='api.bitapai.io', cache_key:bool = True):
        config = self.set_config(kwargs=locals())
        self.conn = http.client.HTTPSConnection(self.config.host)
        self.set_api_key(api_key=config.api_key, cache=config.cache_key)
        
    def set_api_key(self, api_key:str, cache:bool = True):
        if api_key == None:
            api_key = self.get_api_key()

        self.api_key = api_key
        if cache:
            self.add_api_key(api_key)

        assert isinstance(api_key, str)

            
    
    def forward(self, 
                prompt:str,
                count:int = 20,
                return_all:bool = False,
                exclude_unavailable:bool = True,
                uids: list = None,
                api_key:str = None, 
                history:list=None) -> str: 
        api_key = api_key if api_key != None else self.api_key
        
        # build payload
        payload =  {
            'messages': [
                {
                    "role": "system",
                    "content": "You are an AI assistant"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "count": count,
            "return_all": return_all,
            "exclude_unavailable": exclude_unavailable

        }
        if uids is not None:
            payload['uids'] = uids

        if history is not None:
            assert isinstance(history, list)
            assert len(history) > 0
            assert all([isinstance(i, dict) for i in history])
            payload = payload[:1] +  history + payload[1:]


        # make API call to BitAPAI
        payload = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key
        }        
        self.conn.request("POST", "/text", payload, headers)


        # fetch responses
        res = self.conn.getresponse()
        data = res.read().decode("utf-8")
        data = json.loads(data)

        # find non-empty responses in data['choices']
        for i in range(len(data['choices'])):
            if len(data['choices'][i]['message']) > 0 and \
               data['choices'][i]['message']['content'] != '':
                return data['choices'][i]['message']['content']

        return None
    
    chat = ask = forward

    def imagine( self, 
                prompt: str,
                negative_prompt: str = '',
                width: int = 1024,
                height: int = 1024,
                count:int = 20,
                return_all:bool = False,
                exclude_unavailable:bool = True,
                uids: list = None,
                api_key: str = None, 
                history: list=None) -> str: 
        api_key = api_key if api_key != None else self.api_key
        
        # build payload
        payload =  {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "count": count,
            "return_all": return_all,
            "exclude_unavailable": exclude_unavailable,
            "width": width,
            "height": height
        }
        if uids is not None:
            payload['uids'] = uids

        if history is not None:
            assert isinstance(history, list)
            assert len(history) > 0
            assert all([isinstance(i, dict) for i in history])
            payload = payload[:1] +  history + payload[1:]


        # make API call to BitAPAI
        payload = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key
        }
        self.conn.request("POST", "/image", payload, headers)


        # fetch responses
        res = self.conn.getresponse()
        data = res.read().decode("utf-8")
        data = json.loads(data)
        
        assert len(data['choices']) > 0
        
        # find non-empty responses in data['choices']
        for i in range(len(data['choices'])):
            if len(data['choices'][i]['images']) > 0:

                # [display image using gradio]
                # import gradio as gr
                # with gr.Blocks() as demo:
                #     gallery = gr.Gallery()
                #     gallery.value = data['choices'][i]['images']
                #     # im = gr.Image(label="Image Generated by Commune BitAPAI module")
                #     # im.value = Image.open(BytesIO(base64.b64decode(data['choices'][i]['images'][0][23:])))  # exclude preceeding 'data:image/jpeg;base64,'
                # demo.launch(share=True)

                # [display image using streamlit]
                # import streamlit as st
                # st.image(
                #     image=data['choices'][i]['images'][0],
                #     caption="Image Generated by Commune BitAPAI module"
                # )
                
                # [display image using PIL]
                image_data = data['choices'][i]['images'][0].split(',')[1]  # remove the 'data:image/jpeg;base64,' prefix (assuming the base64 encoded image is stored in a variable called 'image_data')
                image_data = bytes(image_data, encoding='utf-8')  # convert to bytes
                img = Image.open(BytesIO(base64.b64decode(image_data)))  # decode and open the image using PIL
                img.show()  # display the image using PIL

                return data['choices'][i]['images'][0]

        return None

