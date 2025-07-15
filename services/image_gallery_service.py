import os
from typing import List

class ImageGalleryService:
    """Servicio simple para obtener imágenes por índice"""
    
    def __init__(self, images_path: str = "images"):
        self.images_path = images_path
    
    def get_images_by_idx(self, idx: int) -> List[str]:
        """Obtiene las 3 imágenes del ave por índice"""
        bird_folder = os.path.join(self.images_path, str(idx))
        
        if not os.path.exists(bird_folder):
            return []
        
        images = []
        for i in range(1, 4):  # 1, 2, 3
            # Buscar con diferentes extensiones
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                image_file = f"{i}{ext}"
                image_path = os.path.join(bird_folder, image_file)
                
                if os.path.exists(image_path):
                    images.append(f"images/{idx}/{image_file}")
                    break
        
        return images
