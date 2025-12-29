# question_generator.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class QwenQuestionGenerator:
    def __init__(self):
        model_name = "ollama run qwen:8b"  # 可替换为本地路径
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            trust_remote_code=True,
            fp16=True  # 若显存不足，可设为 False
        )
        self.model.eval()

    def generate_questions(self, text_chunk):
        prompt = f"""
你是一个教育专家。请根据以下教材内容，生成一道单项选择题（4个选项），并给出正确答案（A/B/C/D）和解析。

教材内容：
{text_chunk}

输出格式（严格按此 JSON 格式）：
{{
  "question": "题目内容",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "A",
  "explanation": "解析内容"
}}
"""
        messages = [{"role": "user", "content": prompt}]
        input_ids = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")
        output = self.model.generate(input_ids, max_new_tokens=512, do_sample=False)
        response = self.tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
        try:
            import json
            return json.loads(response)
        except:
            return None