import torch
import torch.nn as nn
import torchvision
from torchvision.models import vgg16


class ssd(nn.Module):
    def __init__(self, num_cl):
        super(ssd, self).__init__()

        # TODO: Need to add batchnorm for all layers
        new_layers = list(vgg16(pretrained=True).features)
        new_layers[-1] = nn.MaxPool2d(3, 1)

        self.f1 = nn.Sequential(*new_layers[:23])

        self.cl1 = nn.Sequential(
            nn.Conv2d(512, 4*(num_cl + 4), 3),
            nn.ReLU(inplace=True)
        )

        self.base1 = nn.Sequential(*new_layers[23:])

        # The refrence code uses  a dilation of 6 which requires a padding of 6
        self.f2 = nn.Sequential(
            nn.Conv2d(512, 1024, 3, dilation=3, padding=1), 
            nn.ReLU(inplace=True), 
            nn.Conv2d(1024, 1024, 1), 
            nn.ReLU(inplace=True)
        )

        self.cl2 = nn.Sequential(
            nn.Conv2d(1024, 6*(num_cl + 4), 3),
            nn.ReLU(inplace=True)
        )

        self.f3 = nn.Sequential(
            nn.Conv2d(1024, 256, 1), 
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 512, 3, stride=2, padding=1), # This padding is likely wrong
            nn.ReLU(inplace=True)
        )

        self.f4 = nn.Sequential(
            nn.Conv2d(512, 128, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 3, stride=2, padding=1), # This padding is likely wrong
            nn.ReLU(inplace=True)
        )

        self.f5 = nn.Sequential(
            nn.Conv2d(256, 128, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True)
        )

        self.cl5 = nn.Sequential(
            nn.Conv2d(256, 4*(num_cl + 4), 3),
            nn.ReLU(inplace=True)
        )

        self.f6 = nn.Sequential(
            nn.Conv2d(256, 128, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True)
        )

        
    def forward(self, x):

        x1 = self.f1(x)
        x1_2 = self.cl1(x1)

        x1 = self.base1(x1)

        x2 = self.f2(x1)
        x2_2 = self.cl2(x2)

        x3 = self.f3(x2)

        x4 = self.f4(x3)

        x5 = self.f5(x4)
        x5_2 = self.cl5(x5)

        x6 = self.f6(x5)

        return torch.cat([x1_2, x2_2, x3, x4, x5_2, x6], dim=1)


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = ssd(10)
model = model.to(device)

x = torch.zeros((1, 3, 300, 300))
x = x.to(device)

print(model(x))