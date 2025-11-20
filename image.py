from transformers import pipeline
from PIL import Image
from typing import Dict
import os


class ImageProfanityChecker:
    def __init__(self, model_path: str = "Falconsai/nsfw_image_detection"):
        """
        Initialize the image profanity checker.
        
        Args:
            model_path: Hugging Face model identifier for the NSFW detection model
        """
        self.model_path = model_path
        print(f"Loading image detection model from {model_path}...")
        self.classifier = pipeline(
            "image-classification",
            model=model_path,
            device=0  # Use CPU, change to 0 for GPU
        )
        print("Image detection model loaded!")
    
    def check_image(self, image_path: str) -> Dict:
        """
        Check if an image contains profane/NSFW content.
        
        Args:
            image_path: Path to the image file to check
            
        Returns:
            Dictionary containing:
                - is_profane: Boolean indicating if image is NSFW/profane
                - label: The predicted label (nsfw or normal)
                - confidence: Confidence score for the prediction (0-1)
                - all_scores: Dictionary with scores for all classes
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load and classify the image
        image = Image.open(image_path)
        results = self.classifier(image)
        
        # Parse results - results is a list of dicts with 'label' and 'score'
        all_scores = {item['label']: item['score'] for item in results}
        
        # Get the top prediction
        top_prediction = results[0]
        label = top_prediction['label'].lower()
        confidence = top_prediction['score']
        
        # Determine if profane (NSFW)
        is_profane = label == 'nsfw'
        
        return {
            "is_profane": is_profane,
            "label": label,
            "confidence": confidence,
            "all_scores": all_scores
        }