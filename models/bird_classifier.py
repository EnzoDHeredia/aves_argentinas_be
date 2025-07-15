import torch
from torchvision.models import efficientnet_b1
from config import MODEL_PATH, logger

class BirdClassifier:
    def __init__(self, device, num_classes):
        self.device = device
        self.model = self._load_model(num_classes)
        
    def _load_model(self, num_classes):
        """Carga y configura el modelo EfficientNet_B1"""
        model = efficientnet_b1(weights=None)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
        model = model.to(self.device)
        model.eval()
        return model
    
    def predict(self, tensor):
        """Realiza la predicción usando el modelo"""
        with torch.no_grad():
            outputs = self.model(tensor)
            _, predicted = torch.max(outputs, 1)
            confidence = torch.softmax(outputs, dim=1)[0][predicted].item()
        return predicted.item(), confidence
