import json
import ssl
from io import BytesIO
from warnings import filterwarnings, simplefilter

import numpy as np
import torch
import transformers
import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from pydicom import dcmread
from torchvision import transforms

filterwarnings('ignore')
simplefilter(action='ignore', category=FutureWarning)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

api = FastAPI()

if torch.backends.mps.is_available():
    device = torch.device('mps')
elif torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')

ckpt_name = 'aehrc/cxrmate-single-tf'
quantisation_error = True

encoder_decoder = transformers.AutoModel.from_pretrained(ckpt_name, trust_remote_code=True).to(device)
encoder_decoder.eval()
tokenizer = transformers.PreTrainedTokenizerFast.from_pretrained(ckpt_name)
image_processor = transformers.AutoFeatureExtractor.from_pretrained(ckpt_name)

pillow_transforms = transforms.Compose(
    [
        transforms.Resize(size=image_processor.size['shortest_edge']),
        transforms.CenterCrop(size=[
            image_processor.size['shortest_edge'],
            image_processor.size['shortest_edge'],
        ]
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=image_processor.image_mean,
            std=image_processor.image_std,
        ),
    ]
)

dicom_transforms = transforms.Compose(
    [
        transforms.Resize(size=image_processor.size['shortest_edge'], antialias=True),
        transforms.CenterCrop(size=[
            image_processor.size['shortest_edge'],
            image_processor.size['shortest_edge'],
        ]
        ),
        transforms.Normalize(
            mean=image_processor.image_mean,
            std=image_processor.image_std,
        ),
    ]
)


def preprocess_dicom(stream):

    dataset = dcmread(stream)

    image = transforms.ToTensor()(dataset.pixel_array.astype(np.float32))

    min_intensity, max_intensity = image.min(), image.max()

    # See 8.1.1 for more details: https://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_8.1.1
    if ((0x28,0x106) in dataset) and ((0x28,0x107) in dataset):
        min_intensity, max_intensity = dataset[0x28,0x106].value, dataset[0x28,0x107].value

    image = (image - min_intensity) / (max_intensity - min_intensity)

    if quantisation_error:
        image = (255*image).to(torch.uint8).to(torch.float32)/255

    if image.shape[0] == 1:
        image = image.repeat([3, 1, 1])
    image = dicom_transforms(image)
    image = torch.stack([image], dim=0)

    return image

@api.post('/dicom_to_report')
async def image_to_report(request: Request, input_file: UploadFile = File(...)):

    if request.method == 'POST':
        try:

            stream = BytesIO(await input_file.read())
            image = preprocess_dicom(stream)

            outputs = encoder_decoder.generate(
                pixel_values=image.to(device),
                special_token_ids=[tokenizer.sep_token_id],
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                use_cache=True,
                max_length=256,
                num_beams=4,
            )
            outputs.sequences

            findings, impression = encoder_decoder.split_and_decode_sections(
                outputs.sequences,
                [tokenizer.sep_token_id, tokenizer.eos_token_id],
                tokenizer,
            )

            report_dict = {
                'findings': findings,
                'impression': impression,    
            }

            json_results = json.dumps(report_dict)

            return JSONResponse({'data': json_results,
                                 'message': 'Report generation successfully',
                                 'errors': None},
                                status_code=200)
        except Exception as error:
            return JSONResponse({'message': 'Report generation failed',
                                 'errors': 'error'},
                                status_code=400)

@api.post('/image_to_report')
async def image_to_report(request: Request,
                       input_file: UploadFile = File(...)):

    if request.method == 'POST':
        try:

            image = Image.open(BytesIO(await input_file.read()))

            image = pillow_transforms(image)

            image = torch.stack([image], dim=0)

            outputs = encoder_decoder.generate(
                pixel_values=image.to(device),
                special_token_ids=[tokenizer.sep_token_id],
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                use_cache=True,
                max_length=256,
                num_beams=4,
            )
            outputs.sequences

            findings, impression = encoder_decoder.split_and_decode_sections(
                outputs.sequences,
                [tokenizer.sep_token_id, tokenizer.eos_token_id],
                tokenizer,
            )

            report_dict = {
                'findings': findings,
                'impression': impression,    
            }

            json_results = json.dumps(report_dict)

            return JSONResponse({'data': json_results,
                                 'message': 'Report generation successfully',
                                 'errors': None},
                                status_code=200)
        except Exception as error:
            return JSONResponse({'message': 'Report generation failed',
                                 'errors': 'error'},
                                status_code=400)
        
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)