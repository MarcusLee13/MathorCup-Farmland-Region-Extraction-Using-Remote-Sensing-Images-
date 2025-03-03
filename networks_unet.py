import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data
import torch
import config

class conv_block(nn.Module):
    """
    Convolution Block 
    """
    def __init__(self, input_nc, output_nc):
        super(conv_block, self).__init__()
        
        self.conv = nn.Sequential(
            nn.Conv2d(input_nc, output_nc, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(output_nc),
            nn.LeakyReLU(0.2,True),
            nn.Conv2d(output_nc, output_nc, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(output_nc),
            nn.ReLU(inplace=True))

    def forward(self, x):

        x = self.conv(x)
        return x


class up_conv(nn.Module):
    """
    Up Convolution Block
    """
    def __init__(self, input_nc, output_nc):
        super(up_conv, self).__init__()
        self.up = nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.Conv2d(input_nc, output_nc, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(output_nc),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2)
        )

    def forward(self, x):
        x = self.up(x)
        return x


class UnetGenerator(nn.Module):
    """
    UNet - Basic Implementation
    Paper : https://arxiv.org/abs/1505.04597
    """
    def __init__(self, input_nc, output_nc, num_downs, nhf=64, norm_type='none', use_dropout=True, output_function='sigmoid'):
        super(UnetGenerator, self).__init__()

        n1 = 64
        filters = [n1, n1 * 2, n1 * 4, n1 * 8, n1 * 16]
        
        self.Maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.Maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.Maxpool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.Maxpool4 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.Conv1 = conv_block(input_nc, filters[0])
        self.Conv2 = conv_block(filters[0], filters[1])
        self.Conv3 = conv_block(filters[1], filters[2])
        self.Conv4 = conv_block(filters[2], filters[3])
        self.Conv5 = conv_block(filters[3], filters[4])

        self.Up5 = up_conv(filters[4], filters[3])
        self.Up_conv5 = conv_block(filters[4], filters[3])

        self.Up4 = up_conv(filters[3], filters[2])
        self.Up_conv4 = conv_block(filters[3], filters[2])

        self.Up3 = up_conv(filters[2], filters[1])
        self.Up_conv3 = conv_block(filters[2], filters[1])

        self.Up2 = up_conv(filters[1], filters[0])
        self.Up_conv2 = conv_block(filters[1], filters[0])

        self.Conv = nn.Conv2d(filters[0], output_nc, kernel_size=1, stride=1, padding=0)

        # self.gru_layer=nn.GRU(input_size =config.image_size**2,hidden_size =config.image_size**2,batch_first =True,bidirectional=True)

        self.active = torch.nn.Sigmoid()

        self.state=None

        #中间卷积
        # self.Convm1 = conv_block(filters[0], filters[0])
        # self.Convm2 = conv_block(filters[1], filters[1])
        # self.Convm3 = conv_block(filters[2], filters[2])
        # self.Convm4 = conv_block(filters[3], filters[3])

    def forward(self, x):

        e1 = self.Conv1(x)
        
        e2 = self.Maxpool1(e1)
        e2 = self.Conv2(e2)

        e3 = self.Maxpool2(e2)
        e3 = self.Conv3(e3)

        e4 = self.Maxpool3(e3)
        e4 = self.Conv4(e4)

        e5 = self.Maxpool4(e4)
        e5 = self.Conv5(e5)

        d5 = self.Up5(e5)
        d5 = torch.cat((d5), dim=1)

        d5 = self.Up_conv5(d5)

        d4 = self.Up4(d5)
        d4 = torch.cat((d4), dim=1)
        d4 = self.Up_conv4(d4)

        d3 = self.Up3(d4)
        d3 = torch.cat((d3), dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((d2), dim=1)
        d2 = self.Up_conv2(d2)

        out = self.Conv(d2)

        d1 = self.active(out)
        # print(d1.shape)

        # d1,self.state=self.gru_layer(d1.view([1,config.batch_size,config.image_size**2],self.state))
        # print(d1.shape)
        
        # d1=d1.view([config.batch_size*2,1,config.image_size,config.image_size])


        return d1