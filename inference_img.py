import os
import cv2
import torch
import argparse
from torch.nn import functional as F
from model.RIFE import Model
import warnings
warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

parser = argparse.ArgumentParser(description='Interpolation for a pair of images')
parser.add_argument('--img', dest='img', nargs=2, required=True)
parser.add_argument('--exp', default=4, type=int)
args = parser.parse_args()

def fixargs(args):
    for x in args.img:
        if os.path.exists(x):
            continue
        else:
            raise ValueError("%s does not exist " % (x))

def main():
    model = Model()
    loader = model.load_model('./train_log')
    model.eval()
    model.device()
        
    fixargs(args)
    return
    img0 = cv2.imread(args.img[0])
    img1 = cv2.imread(args.img[1])
    img0 = (torch.tensor(img0.transpose(2, 0, 1)).to(device) / 255.).unsqueeze(0)

    img1 = (torch.tensor(img1.transpose(2, 0, 1)).to(device) / 255.).unsqueeze(0)
    n, c, h, w = img0.shape
    ph = ((h - 1) // 32 + 1) * 32
    pw = ((w - 1) // 32 + 1) * 32
    padding = (0, pw - w, 0, ph - h)
    img0 = F.pad(img0, padding)
    img1 = F.pad(img1, padding)

    img_list = [img0, img1]
    for i in range(args.exp):
        tmp = []
        for j in range(len(img_list) - 1):
            mid = model.inference(img_list[j], img_list[j + 1])
            tmp.append(img_list[j])
            tmp.append(mid)
        tmp.append(img1)
        img_list = tmp

    if not os.path.exists('output'):
        os.mkdir('output')
    for i in range(len(img_list)):
        cv2.imwrite('output/img{}.png'.format(i), (img_list[i][0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w])

print(main())
