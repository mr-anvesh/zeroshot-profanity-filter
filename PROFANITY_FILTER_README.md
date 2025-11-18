# Profanity Filter using mDeBERTa-v3-base-mnli-xnli

A zero-shot profanity filter that uses the mDeBERTa-v3-base-mnli-xnli model to detect and censor inappropriate content.

## Features

- **Zero-shot classification**: No need for profanity word lists
- **Multilingual support**: Works with 100+ languages
- **Multiple filtering modes**: Choose between full text censoring, word-level, or aggressive filtering
- **Configurable threshold**: Adjust sensitivity to suit your needs
- **Confidence scores**: Get classification confidence for each prediction

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from profanity_filter import ProfanityFilter

# Initialize the filter
pf = ProfanityFilter(model_path="./", threshold=0.5)

# Filter text
text = "Hello, this is a nice message!"
result = pf.filter(text)

print(result['filtered'])  # Filtered text
print(result['is_profane'])  # True/False
print(result['confidence'])  # Confidence score
```

### Filtering Modes

The filter supports three different modes:

1. **full** (default): Censors the entire text if profanity is detected
   ```python
   result = pf.filter(text, mode="full")
   ```

2. **word**: Attempts to censor at sentence level
   ```python
   result = pf.filter(text, mode="word")
   ```

3. **aggressive**: Replaces profane content with a warning message
   ```python
   result = pf.filter(text, mode="aggressive")
   # Output: "[CONTENT FILTERED: Inappropriate language detected]"
   ```

### Check for Profanity Only

```python
check = pf.is_profane("Some text to check")
print(check['is_profane'])  # Boolean
print(check['confidence'])  # Confidence score
print(check['label'])       # Classification label
```

### Adjust Sensitivity

```python
# More sensitive (lower threshold)
pf = ProfanityFilter(threshold=0.3)

# Less sensitive (higher threshold)
pf = ProfanityFilter(threshold=0.7)
```

## Running the Examples

### Interactive Demo

Run the main profanity filter with interactive mode:

```bash
python profanity_filter.py
```

This will:
1. Show example classifications
2. Enter interactive mode where you can test your own text

### Simple Examples

Run the example usage script:

```bash
python example_usage.py
```

## How It Works

The profanity filter uses zero-shot classification to determine if text contains inappropriate content. It works by:

1. **Classification**: The model classifies text between two categories:
   - "profane, vulgar, obscene, offensive language"
   - "clean, appropriate, respectful language"

2. **Thresholding**: If the "profane" label scores above the threshold, the text is flagged

3. **Censoring**: Flagged text is censored based on the selected mode

## API Reference

### `ProfanityFilter`

#### Constructor
```python
ProfanityFilter(model_path="./", threshold=0.5)
```
- `model_path`: Path to the model directory
- `threshold`: Confidence threshold for profanity detection (0-1)

#### Methods

**`filter(text, mode="full")`**
- Filters text and returns a dictionary with results
- Returns: `{"original": str, "filtered": str, "is_profane": bool, "confidence": float, "label": str}`

**`is_profane(text)`**
- Checks if text contains profanity
- Returns: `{"is_profane": bool, "confidence": float, "label": str}`

**`censor_word(word)`**
- Censors a single word
- Returns: Censored word string

**`censor_text(text, aggressive=False)`**
- Censors entire text
- Returns: Censored text string

## Performance Notes

- First run will be slower as the model loads
- CPU inference is used by default (change `device=-1` to `device=0` for GPU)
- Processing time depends on text length

## Limitations

- Zero-shot classification may have false positives/negatives
- Context-dependent profanity may not be caught
- Threshold tuning may be needed for specific use cases
- Model requires ~500MB of memory

## License

This code is provided as-is. The underlying model (mDeBERTa-v3-base-mnli-xnli) is licensed under MIT.
