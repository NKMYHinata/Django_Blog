from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from transformers import GPT2LMHeadModel, GPT2Tokenizer, BertTokenizer
import torch
import json

# 加载模型和分词器
model = GPT2LMHeadModel.from_pretrained('uer/gpt2-chinese-cluecorpussmall')
tokenizer = BertTokenizer.from_pretrained('uer/gpt2-chinese-cluecorpussmall')


@method_decorator(csrf_exempt, name='dispatch')  # 应用方法到所有请求上
class IndexView(View):
    def get(self, request):
        return render(request, 'chat.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            print('message', message)
            inputs = tokenizer.encode(message, return_tensors='pt')

            # 设置生成参数
            reply_ids = model.generate(
                inputs,
                max_length=50,
                num_return_sequences=1,
                no_repeat_ngram_size=2,  # 防止重复
                do_sample=True,
                top_k=50,
                top_p=0.95
            )
            reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
            return JsonResponse({'reply': reply})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
