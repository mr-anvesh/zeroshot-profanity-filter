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
    
    def __init__(self, model_path: str = "Anvesh18/zeroshot-profanity-filter", threshold: float = 0.5):
        """
        Initialize the profanity filter.
        
        Args:
            model_path: Path to the model directory or Hugging Face model identifier
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
        
        # Binary classification labels
        self.profanity_labels = [
            "profane",
            "non-profane"
        ]
    
    def is_profane(self, text: str) -> Dict:
        """
        Check if the text contains profanity.
        
        Args:
            text: Input text to check
            
        Returns:
            Dictionary containing:
                - is_profane: Boolean indicating if text is profane
                - profane_probability: Probability of being profane (0-1)
                - non_profane_probability: Probability of being non-profane (0-1)
                - label: The predicted label
        """
        if not text or not text.strip():
            return {
                "is_profane": False,
                "profane_probability": 0.0,
                "non_profane_probability": 1.0,
                "label": "non-profane"
            }
        
        result = self.classifier(text, self.profanity_labels)
        
        # Get probabilities for both labels
        labels = result["labels"]
        scores = result["scores"]
        
        # Create a mapping of label to score
        label_scores = dict(zip(labels, scores))
        profane_prob = label_scores.get("profane", 0.0)
        non_profane_prob = label_scores.get("non-profane", 0.0)
        
        # Determine if profane based on threshold
        is_profane = profane_prob >= self.threshold
        predicted_label = "profane" if is_profane else "non-profane"
        
        return {
            "is_profane": is_profane,
            "profane_probability": profane_prob,
            "non_profane_probability": non_profane_prob,
            "label": predicted_label
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
            "profane_probability": check_result["profane_probability"],
            "non_profane_probability": check_result["non_profane_probability"],
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
        print(f"Profane: {result['is_profane']}")
        print(f"Profane Probability: {result['profane_probability']:.3f}")
        print(f"Non-Profane Probability: {result['non_profane_probability']:.3f}")
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
        print(f"Classification: {result['label']}")
        print(f"Profane: {result['profane_probability']:.3f} | Non-Profane: {result['non_profane_probability']:.3f}\n")


if __name__ == "__main__":
    main()
