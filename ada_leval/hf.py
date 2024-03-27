import os
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor
import copy as cp
import os.path as osp
import torch.nn as nn
import torch
from .smp import *

def get_gpu_num(model_name):
    model_name = model_name.lower()
    kws = {
        8: ['65b', '70b'],
        4: ['30b', '33b', '35b', '40b'],
        2: ['13b', '14b', '20b'],
        1: ['6b', '7b', 'moss'],
    }
    for k in [8, 4, 2, 1]:
        for keyword in kws[k]:
            if keyword in model_name:
                return k
    return 8

model_map = {
    'internlm2-7b': 'internlm/internlm2-chat-7b',
    'internlm2-20b': 'internlm/internlm2-chat-20b',
    'qwen-7b-v1.5': 'Qwen/Qwen1.5-7B-Chat',
    'qwen-14b-v1.5': 'Qwen/Qwen1.5-14B-Chat',
    'qwen-72b-v1.5': 'Qwen/Qwen1.5-72B-Chat', 
    'vicuna-13b-v1.5':'lmsys/vicuna-13b-v1.5',
    'vicuna-7b-v1.5':'lmsys/vicuna-7b-v1.5', 
    'yi-6b': '01-ai/Yi-6B-Chat', 
    'yi-34b': '01-ai/Yi-34B-Chat', 
    'mistral-7b': 'mistralai/Mistral-7B-v0.1'
}

class HFChatModel:

    is_api = False

    def _get_context_length(self, model, model_path):
        # By default, we use model.config.seq_length
        model_path = model_path.lower()
        context_window = model.config.max_position_embeddings
        return context_window
    
    def _get_context_length_robust(self, model, model_path):
        try:
            context_window = self._get_context_length(model, model_path)
            return context_window
        except:
            warnings.warn(
                "Failed to extract context_window information from config / generation_config. "
                "Please read the above code and check if the logic works for you model path"
            )
            raise NotImplementedError
        
    def __init__(self, 
                 model_path, 
                 system_prompt: str=None,
                 **model_kwargs):
        
        if 'vicuna' in model_path.lower():
            try:
                from fastchat.model import get_conversation_template
            except:
                warnings.warn("Please install fastchat first to use vicuna. ")

        from transformers import AutoTokenizer, AutoModelForCausalLM
        from transformers.generation import GenerationConfig
        
        if model_path in model_map:
            model_path = model_map[model_path]
        self.model_path = model_path
        LoadModel = AutoModelForCausalLM
        assert osp.exists(model_path) or len(model_path.split('/')) == 2

        device = model_kwargs.pop('device', 'auto')
        if device == None:
            device = 'auto'
            
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if 'internlm' in model_path.lower():
            model = LoadModel.from_pretrained(
                model_path, trust_remote_code=True, torch_dtype=torch.float16, device_map='cpu')
        else:
            model = LoadModel.from_pretrained(model_path, trust_remote_code=True, device_map='cpu')

        model = model.eval()
        
        if device in ['auto', 'cuda']:
            model = model.to('cuda')
        elif device == 'cpu':
            pass
        elif isinstance(device, int):
            model = model.to(f'cuda:{device}')
        elif isinstance(device, list):
            no_split = []
            if 'internlm' in model_path.lower():
                no_split = ['InternLM2DecoderLayer']
            for i in range(1, 81):
                from accelerate import dispatch_model, infer_auto_device_map
                max_memory = {g: f'{i}GiB' for g in device}
                device_map = infer_auto_device_map(model, max_memory, no_split_module_classes=no_split)
                if 'disk' not in device_map.values():
                    model = dispatch_model(model, device_map)
                    break
                if i == 80:
                    exit(1)

        try:
            model.generation_config = GenerationConfig.from_pretrained(model_path, trust_remote_code=True, device_map=device)
        except:
            pass

        torch.cuda.empty_cache()
        self.model = model
        self.context_length = self._get_context_length_robust(model=model, model_path=model_path)
        self.answer_buffer = 128
        self.system_prompt = system_prompt
        default_kwargs = {
            'do_sample': False
        }
        default_kwargs.update(model_kwargs)

        for k, v in default_kwargs.items():
            warnings.warn(f'Following args will be used for inference, {k}: {v}. ')
        self.kwargs = default_kwargs
        torch.cuda.empty_cache()
        
    def generate(self, input):
        if 'vicuna' in self.model_path.lower():
            from fastchat.model import get_conversation_template
            conv = get_conversation_template('vicuna')
            conv.append_message(conv.roles[0], input)
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()
            inputs = self.tokenizer([prompt], return_tensors="pt")
            if torch.cuda.is_available():
                for k in inputs:
                    inputs[k] = inputs[k].cuda()
            kwargs = dict(do_sample=True, temperature=0.7, repetition_penalty=1.0, max_new_tokens=512)
            kwargs.update(self.kwargs)
            outputs = self.model.generate(**inputs, **kwargs)
            resp = self.tokenizer.decode(outputs[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True, spaces_between_special_tokens=False)
        elif 'qwen' in self.model_path.lower():
            prompt = input
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            model_inputs = self.tokenizer([text], return_tensors="pt").to('cuda')

            generated_ids = self.model.generate(model_inputs.input_ids, **self.kwargs)
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            resp = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        elif '01-ai' in self.model_path.lower():
            messages = [{'role': 'user', 'content': 'hi'}]
            input_ids = self.tokenizer.apply_chat_template(conversation=messages, tokenize=True, add_generation_prompt=True, return_tensors='pt')
            output_ids = self.model.generate(input_ids.to('cuda'))
            resp = self.tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
        elif 'mistralai' in self.model_path.lower():
            text = f'<s>[INST] {input} [/INST]'
            encoded = self.tokenizer(text, return_tensors='pt', add_special_tokens=False).to('cuda')
            generated_ids = self.model.generate(**encoded, **self.kwargs)
            decoded = self.tokenizer.batch_decode(generated_ids)
            resp = decoded[0]
            resp = resp.strip().split('</s>')[0].strip()
        else:
            resp, _ = self.model.chat(self.tokenizer, input, history=[], **self.kwargs)
        torch.cuda.empty_cache()
        return resp

    def length_ok(self, inputs):
        tot = len(self.tokenizer.encode(self.system_prompt)) if self.system_prompt is not None else 0
        for s in inputs:
            tot += len(self.tokenizer.encode(s))
        return tot + self.answer_buffer < self.context_length