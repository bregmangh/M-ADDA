"""Dataset setting and data loader for USPS.

Modified from
https://github.com/mingyuliutw/CoGAN/blob/master/cogan_pytorch/src/dataset_usps.py
"""

import gzip
import os
import pickle
import urllib

import numpy as np
import torch
import torch.utils.data as data
from torchvision import datasets, transforms



class USPS(data.Dataset):
    url = "https://raw.githubusercontent.com/mingyuliutw/CoGAN/master/cogan_pytorch/data/uspssample/usps_28x28.pkl"

    def __init__(self, root, split, transform=None, download=False):
        """Init USPS dataset."""
        # init params
        self.split=split
        self.root = os.path.expanduser(root)
        self.filename = "usps_28x28.pkl"

        # Num of Train = 7438, Num ot Test 1860
        self.transform = transform
        self.dataset_size = None

        # download dataset.
        if download:
            self.download()
        if not self._check_exists():
            raise RuntimeError("Dataset not found." +
                               " You can use download=True to download it")

        self.X, self.y = self.load_samples()
        if self.split=="train":
            total_num_samples = self.y.shape[0]
            indices = np.arange(total_num_samples)
            np.random.shuffle(indices)
            self.X = self.X[indices[0:self.dataset_size], ::]
            self.y = self.y[indices[0:self.dataset_size]]
            
            n_usps = self.y.shape[0]
            np.random.seed(1)
            ind =  np.random.choice(n_usps, 1800, replace=False)

            self.X = self.X[ind]
            self.y = self.y[ind]

            self.dataset_size = self.y.shape[0]
        

        self.X = torch.FloatTensor(self.X)
        self.y = torch.LongTensor(self.y)

    def __getitem__(self, index):
        """Get images and target for data loader.

        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, label = self.X[index].clone(), self.y[index].clone()
        
        if self.transform is not None:
            img = self.transform(img)
        
        return img, label

    def __len__(self):
        """Return size of dataset."""
        return self.dataset_size

    def _check_exists(self):
        """Check if dataset is download and in right place."""
        return os.path.exists(os.path.join(self.root, self.filename))

    def download(self):
        """Download dataset."""
        filename = os.path.join(self.root, self.filename)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        if os.path.isfile(filename):
            return
        print("Download %s to %s" % (self.url, os.path.abspath(filename)))
        urllib.request.urlretrieve(self.url, filename)
        print("[DONE]")
        return

    def load_samples(self):
        """Load sample images from dataset."""
        filename = os.path.join(self.root, self.filename)
        f = gzip.open(filename, "rb")
        data_set = pickle.load(f, encoding="bytes")
        f.close()
        if self.split == "train":
            images = data_set[0][0]
            labels = data_set[0][1]
            self.dataset_size = labels.shape[0]
        elif self.split == "val":            
            images = data_set[1][0]
            labels = data_set[1][1]
            self.dataset_size = labels.shape[0]
        return images, labels


def get_usps(split, batch_size=50):
    """Get USPS dataset loader."""
    # image pre-processing
    pre_process = transforms.Compose([transforms.Normalize(
                                          mean=[0.5,0.5,0.5],
                                          std=[0.5,0.5,0.5])])

    # dataset and data loader
    usps_dataset = USPS(root="data",
                        split=split,
                        transform=pre_process,
                        download=True)

    usps_data_loader = torch.utils.data.DataLoader(
        dataset=usps_dataset,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True)

    return usps_data_loader