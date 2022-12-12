import os
from torch.utils.data import Dataset
from PIL import Image





class StreetDataset(Dataset):

    def __init__(self, df, file_dir, transform=None):

        # -- define path to images ---------------------------------------------------------------------
        self.img_dir = file_dir

        # -- define image names ------------------------------------------------------------------------
        self.img_names = df["Name"]

        # -- define numeric labels ---------------------------------------------------------------------
        self.y = df["image_score"]

        # -- specify transforms ------------------------------------------------------------------------
        self.transform = transform

    def __getitem__(self, index):
        # -- get image ---------------------------------------------------------------------------------
        img = Image.open(os.path.join(self.img_dir,
                                      self.img_names[index])
                         )

        # -- transform image ---------------------------------------------------------------------------
        if self.transform is not None:
            img = self.transform(img)

        # -- get image label and image name ------------------------------------------------------------
        label = self.y[index]
        img_name = self.img_names[index]

        return img, label, img_name

    def __len__(self):
        return self.y.shape[0]
