import os, torch, transformers
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms
from io import BytesIO
from torchvision.utils import make_grid

def generate_medical_description(image_path):
    ckpt_name = 'aehrc/medicap'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load the model, tokenizer, and image processor
    encoder_decoder = transformers.AutoModel.from_pretrained(ckpt_name, trust_remote_code=True).to(device)
    encoder_decoder.eval()
    image_processor = transformers.AutoFeatureExtractor.from_pretrained(ckpt_name)
    tokenizer = transformers.PreTrainedTokenizerFast.from_pretrained(ckpt_name)

    # Define image transforms
    test_transforms = transforms.Compose(
        [
            transforms.Resize(size=image_processor.size['shortest_edge']),
            transforms.CenterCrop(size=[
                image_processor.size['shortest_edge'],
                image_processor.size['shortest_edge'],
            ]),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=image_processor.image_mean,
                std=image_processor.image_std,
            ),
        ]
    )

    # Load and process the image
    image = Image.open(image_path).convert('RGB')
    image = test_transforms(image)
    image = torch.unsqueeze(image, dim=0)

    # Generate description
    outputs = encoder_decoder.generate(
        pixel_values=image.to(device),
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        return_dict_in_generate=True,
        use_cache=True,
        max_length=256,
        num_beams=4,
    )

    # Decode the output
    description = tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
    
    return description

