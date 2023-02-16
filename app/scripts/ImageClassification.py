import os
import torch
from torchvision import transforms

from settings import MODEL_URL

STREETVIEW_URL = os.path.join(MODEL_URL, "streetview")

streetview_model_neutral = torch.load(os.path.join(STREETVIEW_URL, "streetview_model_neutral.pt"))
streetview_model_positive = torch.load(os.path.join(STREETVIEW_URL, "streetview_model_positive.pt"))
streetview_model_very_positive = torch.load(os.path.join(STREETVIEW_URL, "streetview_model_very_positive.pt"))
streetview_model_negative = torch.load(os.path.join(STREETVIEW_URL, "streetview_model_negative.pt"))
streetview_model_very_negative = torch.load(os.path.join(STREETVIEW_URL, "streetview_model_very_negative.pt"))

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
IMG_SIZE = (224, 224)

test_transform = transforms.Compose([transforms.Resize(size=IMG_SIZE),
                                     transforms.ToTensor(),
                                     transforms.Normalize(mean=MEAN, std=STD)
                                     ])


def score_image(img):
    img = test_transform(img).unsqueeze(0)

    score_neutral = round(streetview_model_neutral(img).item(),1)
    score_positive = round(streetview_model_positive(img).item(),1)
    score_very_positive = round(streetview_model_very_positive(img).item(),1)
    score_negative = round(streetview_model_negative(img).item(),1)
    score_very_negative = round(streetview_model_very_negative(img).item(),1)

    return score_neutral, score_positive, score_very_positive, score_negative, score_very_negative
