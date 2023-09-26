from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("models/THUDM/chatglm-6b-int4", trust_remote_code=True)
model = AutoModel.from_pretrained("models/THUDM/chatglm-6b-int4", trust_remote_code=True).float()
response, history = model.chat(tokenizer, "你好", history=[])
print(response)