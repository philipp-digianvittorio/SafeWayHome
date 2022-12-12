
import os
import numpy as np
import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights

from model_training.scripts.Functions import model_training, evaluate
from model_training.scripts.Datasets import StreetDataset

################################################################################################
### -- Parameter Settings ------------------------------------------------------------------ ###
################################################################################################
BASE_DIR = r"C:\users\philipp\documents\studium\master\4. semester\ds project\safewayhome"
INPUT_FILE = os.path.join(BASE_DIR, r"model_training\data\ratings.csv")
IMAGE_DIR = os.path.join(BASE_DIR, r"model_training\data\images")

RANDOM_SEED = 8
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_OUTPUT_URL = os.path.join(BASE_DIR, r"models\streetview_model.pt")

NUM_CLASSES = 5
LEARNING_RATE = 2e-5  # use a small learning rate because model is already trained
NUM_EPOCHS = 30

IMG_SIZE = (224, 224)
BATCH_SIZE = 64

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


################################################################################################
### -- Create Datasets --------------------------------------------------------------------- ###
################################################################################################
ratings = pd.read_csv(INPUT_FILE)
ratings["image_score"] = ratings["image_score"].round(0).astype(np.int64) - 1
train_df = ratings.sample(frac=0.7, random_state=RANDOM_SEED)
valid_df = ratings.drop(train_df.index).sample(frac=0.5, random_state=RANDOM_SEED)
test_df = ratings.drop(train_df.index).drop(valid_df.index)

train_df, valid_df, test_df = train_df.reset_index(drop=True), test_df.reset_index(drop=True), valid_df.reset_index(drop=True)

################################################################################################
### -- Create Dataloaders ------------------------------------------------------------------ ###
################################################################################################

# -- train and test transforms -----------------------------------------------------------------
train_transform = transforms.Compose([transforms.Resize(size=IMG_SIZE),
                                      transforms.RandomHorizontalFlip(p=0.2),
                                      transforms.RandomRotation(degrees=10),
                                      transforms.RandomResizedCrop(size=IMG_SIZE, scale=(0.9,1)),
                                      transforms.ToTensor(),
                                      transforms.Normalize(mean=MEAN, std=STD)
                                      ])

test_transform = transforms.Compose([transforms.Resize(size=IMG_SIZE),
                                     transforms.ToTensor(),
                                     transforms.Normalize(mean=MEAN, std=STD)
                                    ])

# -- train dataset and loader ------------------------------------------------------------------
train_dataset = StreetDataset(df=train_df,
                                       file_dir=IMAGE_DIR,
                                       transform=train_transform)

TRAIN_LOADER = DataLoader(dataset=train_dataset,
                          batch_size=BATCH_SIZE,
                          shuffle=True,
                          drop_last=True)
                          #num_workers=2)

# -- validation dataset and loader -------------------------------------------------------------
valid_dataset = StreetDataset(df=valid_df,
                                       file_dir=IMAGE_DIR,
                                       transform=test_transform)

VALID_LOADER = DataLoader(dataset=valid_dataset,
                          batch_size=BATCH_SIZE,
                          shuffle=False)
                          #num_workers=2)

# -- test dataset and loader -------------------------------------------------------------------
test_dataset = StreetDataset(df=test_df,
                                      file_dir=IMAGE_DIR,
                                      transform=test_transform)

TEST_LOADER = DataLoader(dataset=test_dataset,
                         batch_size=BATCH_SIZE,
                         shuffle=False)
                         #num_workers=2)

################################################################################################
### -- Load Pre-Trained Model -------------------------------------------------------------- ###
################################################################################################

# -- Load pre-trained ResNet model -------------------------------------------------------------
MODEL = resnet18(weights=ResNet18_Weights.DEFAULT)
print(MODEL)
'''
# get list of models
torch.hub.list('zhanghang1989/ResNeSt', force_reload=True)
# load pretrained models, using ResNeSt-50 as an example
MODEL = torch.hub.load('zhanghang1989/ResNeSt', 'resnest50', pretrained=True)

'''
# get number of input features for last layer
IN_FEATURES = MODEL.fc.in_features

# replace last layer by custom layer with different number of output features
final_fc = nn.Linear(IN_FEATURES, NUM_CLASSES)
MODEL.fc = final_fc
print(MODEL.fc)


# -- freeze all model parameters that should not be fine-tuned ---------------------------------
for parameter in MODEL.conv1.parameters():
  parameter.requires_grad = False

for parameter in MODEL.bn1.parameters():
  parameter.requires_grad = False

for parameter in MODEL.layer1.parameters():
    parameter.requires_grad = False

for parameter in MODEL.layer2.parameters():
    parameter.requires_grad = False

for parameter in MODEL.layer3.parameters():
    parameter.requires_grad = False

for parameter in MODEL.layer4[0].parameters():
    parameter.requires_grad = False


################################################################################################
### -- Model Training ---------------------------------------------------------------------- ###
################################################################################################

# -- set train parameters ----------------------------------------------------------------------
OPTIMIZER = torch.optim.Adam(MODEL.parameters(), lr=LEARNING_RATE)

CRITERION = nn.CrossEntropyLoss()
CRITERION = CRITERION.to(DEVICE)

MODEL = MODEL.to(DEVICE)

# -- train the model ---------------------------------------------------------------------------
acc_trend, loss_trend = model_training(NUM_EPOCHS, TRAIN_LOADER, VALID_LOADER, MODEL, CRITERION, OPTIMIZER, DEVICE, MODEL_OUTPUT_URL)

################################################################################################
### -- Test Model Performance -------------------------------------------------------------- ###
################################################################################################

OPT_MODEL = torch.load(MODEL_OUTPUT_URL + "model.pt")

test_loss, test_acc = evaluate(OPT_MODEL, TEST_LOADER, CRITERION, DEVICE)
print(f"test loss: {test_loss: .4f}")
print(f"test acc.: {100*test_acc: .2f} %")


################################################################################################
### -- Predict Image Scores ---------------------------------------------------------------- ###
################################################################################################
from PIL import Image

im = Image.open(os.path.join(IMAGE_DIR, "Adelonstrasse_65929.jpeg"))
scores = torch.nn.functional.softmax(OPT_MODEL(test_transform(im).unsqueeze(0))[0])
print(scores)