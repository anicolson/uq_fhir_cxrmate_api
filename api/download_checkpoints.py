import transformers

ckpt_name = 'aehrc/cxrmate-single-tf'

encoder_decoder = transformers.AutoModel.from_pretrained(ckpt_name, trust_remote_code=True)
tokenizer = transformers.PreTrainedTokenizerFast.from_pretrained(ckpt_name)
image_processor = transformers.AutoFeatureExtractor.from_pretrained(ckpt_name)