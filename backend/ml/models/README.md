# ML Models Directory

This directory contains trained machine learning models for the Smart Trading Journal.

## Models Not Included in Git

Due to file size limitations on GitHub, the following models are not included in this repository:

- `finbert_trading_vi/` - Fine-tuned FinBERT model for Vietnamese financial text (~3GB)
- `feature_scaler.pkl` - Feature scaling model for behavioral analysis

## How to Get the Models

### Option 1: Download Pre-trained Models
Download from [Google Drive/Hugging Face - Add your link here]

### Option 2: Train Your Own Models

#### Train FinBERT Model:
```bash
# From project root
python backend/ml/training/train_nlp.py
```

#### Train Behavioral Classifier:
```bash
python backend/ml/behavioral/train_classifier.py
```

## Model Files Structure

After downloading or training, your directory should look like:
```
models/
├── README.md (this file)
├── behavioral_classifier.json
├── feature_scaler.pkl
└── finbert_trading_vi/
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    ├── vocab.txt
    └── ...
```

## Training Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+
- 16GB+ RAM recommended
- GPU with 8GB+ VRAM (for FinBERT training)

## Model Details

### FinBERT Trading Vietnamese
- Base Model: PhoNLP/PhoBERT
- Fine-tuned on Vietnamese financial news
- Task: Sentiment analysis for trading
- Accuracy: ~85-90%

### Behavioral Classifier
- Algorithm: Random Forest
- Features: Trading patterns, timing, emotions
- Task: Detect FOMO, Revenge trading, Tilt
- Accuracy: ~82%

## Notes

- Models are stored locally and not pushed to GitHub
- Keep models updated with latest training data
- Backup important model checkpoints
