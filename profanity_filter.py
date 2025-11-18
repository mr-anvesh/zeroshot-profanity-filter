"""
Profanity Filter using mDeBERTa-v3-base-mnli-xnli Zero-Shot Classifier

This module provides a profanity filter that uses zero-shot classification
to detect and censor profane content.
"""

from transformers import pipeline
import re
from typing import Dict, List


class ProfanityFilter:
    """
    A profanity filter that uses zero-shot classification to detect
    and censor profane content.
    """
    
    def __init__(self, model_path: str = "./", threshold: float = 0.5):
        """
        Initialize the profanity filter.
        
        Args:
            model_path: Path to the model directory
            threshold: Confidence threshold for profanity detection (0-1)
        """
        self.threshold = threshold
        print(f"Loading model from {model_path}...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_path,
            device=-1  # Use CPU, change to 0 for GPU
        )
        print("Model loaded successfully!")
        
        # Common profanity categories for classification
        self.profanity_labels = [
            "profane, vulgar, obscene, offensive language",
            "clean, appropriate, respectful language"
        ]
    
    def is_profane(self, text: str) -> Dict:
        """
        Check if the text contains profanity.
        
        Args:
            text: Input text to check
            
        Returns:
            Dictionary containing:
                - is_profane: Boolean indicating if text is profane
                - confidence: Confidence score for the classification
                - label: The predicted label
        """
        if not text or not text.strip():
            return {
                "is_profane": False,
                "confidence": 0.0,
                "label": "clean, appropriate, respectful language"
            }
        
        result = self.classifier(text, self.profanity_labels)
        
        # Get the top prediction
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        is_profane = (
            "profane" in top_label.lower() and 
            top_score >= self.threshold
        )
        
        return {
            "is_profane": is_profane,
            "confidence": top_score,
            "label": top_label
        }
    
    def censor_word(self, word: str) -> str:
        """
        Censor a word by replacing characters with asterisks.
        Keeps first and last character visible if word is long enough.
        
        Args:
            word: Word to censor
            
        Returns:
            Censored word
        """
        if len(word) <= 2:
            return '*' * len(word)
        elif len(word) <= 4:
            return word[0] + '*' * (len(word) - 1)
        else:
            return word[0] + '*' * (len(word) - 2) + word[-1]
    
    def censor_text(self, text: str, aggressive: bool = False) -> str:
        """
        Censor the entire text by replacing it with asterisks or a message.
        
        Args:
            text: Text to censor
            aggressive: If True, replace with warning message instead of asterisks
            
        Returns:
            Censored text
        """
        if aggressive:
            return "[CONTENT FILTERED: Inappropriate language detected]"
        
        # Preserve sentence structure but censor words
        words = text.split()
        censored_words = [self.censor_word(word) for word in words]
        return ' '.join(censored_words)
    
    def filter(self, text: str, mode: str = "full") -> Dict:
        """
        Filter text for profanity and return appropriate output.
        
        Args:
            text: Input text to filter
            mode: Filtering mode:
                - "full": Censor entire text if profane
                - "word": Attempt to censor individual words (basic implementation)
                - "aggressive": Replace with warning message
                
        Returns:
            Dictionary containing:
                - original: Original text
                - filtered: Filtered/censored text
                - is_profane: Whether profanity was detected
                - confidence: Confidence score
                - label: Classification label
        """
        check_result = self.is_profane(text)
        
        if check_result["is_profane"]:
            if mode == "aggressive":
                filtered_text = self.censor_text(text, aggressive=True)
            elif mode == "word":
                # Basic word-level censoring - check each sentence
                filtered_text = self._censor_by_sentence(text)
            else:  # mode == "full"
                filtered_text = self.censor_text(text, aggressive=False)
        else:
            filtered_text = text
        
        return {
            "original": text,
            "filtered": filtered_text,
            "is_profane": check_result["is_profane"],
            "confidence": check_result["confidence"],
            "label": check_result["label"]
        }
    
    def _censor_by_sentence(self, text: str) -> str:
        """
        Attempt to censor text at sentence level.
        
        Args:
            text: Input text
            
        Returns:
            Text with profane sentences censored
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+\s*)', text)
        filtered_sentences = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip() and not re.match(r'^[.!?\s]+$', sentence):
                result = self.is_profane(sentence)
                if result["is_profane"]:
                    filtered_sentences.append(self.censor_text(sentence, aggressive=False))
                else:
                    filtered_sentences.append(sentence)
            else:
                filtered_sentences.append(sentence)
        
        return ''.join(filtered_sentences)


def main():
    """
    Example usage of the ProfanityFilter.
    """
    # Initialize the filter
    filter = ProfanityFilter(model_path="./", threshold=0.5)
    
    # Test examples
    test_texts = [
        "This is a nice and friendly message.",
        "What a beautiful day to write some code!",
        "I love programming and building cool projects.",
    ]
    
    print("\n" + "="*70)
    print("PROFANITY FILTER DEMO")
    print("="*70 + "\n")
    
    for text in test_texts:
        print(f"Input: {text}")
        result = filter.filter(text, mode="full")
        print(f"Filtered: {result['filtered']}")
        print(f"Profane: {result['is_profane']} (confidence: {result['confidence']:.2f})")
        print(f"Label: {result['label']}")
        print("-" * 70 + "\n")
    
    # Interactive mode
    print("\n" + "="*70)
    print("INTERACTIVE MODE - Enter text to filter (or 'quit' to exit)")
    print("="*70 + "\n")
    
    while True:
        user_input = input("Enter text: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        result = filter.filter(user_input, mode="full")
        print(f"\nFiltered output: {result['filtered']}")
        print(f"Classification: {result['label']} (confidence: {result['confidence']:.2f})\n")


if __name__ == "__main__":
    main()
