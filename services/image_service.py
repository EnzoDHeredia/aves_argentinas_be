from torchvision import transforms
from config import IMG_SIZE

class ImageProcessor:
    def __init__(self, device):
        self.device = device
        self.transform = transforms.Compose([
            transforms.Resize(IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def preprocess_image(self, img):
        """Preprocesa la imagen para el modelo"""
        return self.transform(img).unsqueeze(0).to(self.device)
