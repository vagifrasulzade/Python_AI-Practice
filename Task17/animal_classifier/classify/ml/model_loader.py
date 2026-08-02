import torch
import torch.nn.functional as F

from torchvision import models,transforms
from PIL import Image


class ImageNetClassifier:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # 2ci qrup - EfficientNet-B0
        weights  = models.EfficientNet_B0_Weights.DEFAULT

        self.model = models.efficientnet_b0(weights=weights)

        self.model.eval()

        self.model.to(self.device)

        self.idx_to_label = weights.meta["categories"]

        self.transform = weights.transforms()

    def predict(self,image_path,topk=5):
        image = Image.open(image_path).convert("RGB")
        img_t = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(img_t)
            probs = F.softmax(output,dim=1)[0]

        top_probs, top_idxs = torch.topk(probs,topk)

        top_probs = top_probs.cpu().numpy()
        top_idxs = top_idxs.cpu().numpy()

        results = []

        for p,idx in zip(top_probs,top_idxs):
            label = self.idx_to_label[idx]
            results.append((label,float(p*100)))

        return results