"""
Data Augmentation Utilities for NLP Training
Provides techniques to expand small datasets
"""

import random
from typing import List, Dict
import re


class TextAugmentor:
    """
    Text augmentation for Vietnamese and English trading notes.
    Techniques: synonym replacement, random insertion/deletion, back-translation simulation.
    """
    
    def __init__(self):
        # Vietnamese synonyms for trading terms
        self.vn_synonyms = {
            "mua": ["vào lệnh", "entry", "open position", "long"],
            "bán": ["chốt", "exit", "close", "short"],
            "lời": ["profit", "win", "thắng", "dương"],
            "lỗ": ["loss", "thua", "âm", "red"],
            "phân tích": ["analysis", "check", "xem xét", "đánh giá"],
            "kế hoạch": ["plan", "chiến lược", "strategy"],
            "stop loss": ["sl", "cắt lỗ", "stoploss"],
            "take profit": ["tp", "chốt lời", "target"],
            "all in": ["full port", "toàn bộ vốn", "hết vốn"],
            "sợ lỡ": ["fomo", "fear of missing out", "miss cơ hội"],
            "tham": ["greedy", "greed", "탐욕"],
            "sợ": ["fear", "lo", "lo lắng", "panic"]
        }
        
        # English synonyms
        self.en_synonyms = {
            "buy": ["long", "enter", "open position"],
            "sell": ["short", "exit", "close"],
            "profit": ["gain", "win", "earnings"],
            "loss": ["losing", "negative", "red"],
            "analyze": ["check", "review", "examine"],
            "plan": ["strategy", "approach", "scheme"],
            "stop loss": ["sl", "stop"],
            "take profit": ["tp", "target", "goal"],
            "fomo": ["fear of missing out", "missing out"],
            "greed": ["greedy", "avaricious"],
            "fear": ["scared", "afraid", "worried"]
        }
    
    def synonym_replacement(self, text: str, language: str = "vi", n: int = 1) -> str:
        """
        Replace n random words with their synonyms.
        
        Args:
            text: Input text
            language: "vi" or "en"
            n: Number of words to replace
            
        Returns:
            Augmented text
        """
        synonyms = self.vn_synonyms if language == "vi" else self.en_synonyms
        words = text.split()
        
        # Find replaceable words
        replaceable_indices = []
        for i, word in enumerate(words):
            word_lower = word.lower().strip(".,!?;:")
            if word_lower in synonyms:
                replaceable_indices.append((i, word_lower))
        
        if not replaceable_indices:
            return text
        
        # Randomly select n words to replace
        num_replacements = min(n, len(replaceable_indices))
        to_replace = random.sample(replaceable_indices, num_replacements)
        
        # Perform replacements
        for idx, original_word in to_replace:
            synonym_list = synonyms[original_word]
            synonym = random.choice(synonym_list)
            words[idx] = synonym
        
        return " ".join(words)
    
    def random_insertion(self, text: str, language: str = "vi", n: int = 1) -> str:
        """
        Randomly insert n common filler words.
        
        Args:
            text: Input text
            language: "vi" or "en"
            n: Number of insertions
            
        Returns:
            Augmented text
        """
        fillers = {
            "vi": ["thì", "nhé", "đó", "ạ", "nha", "đây", "này"],
            "en": ["well", "so", "actually", "basically", "just", "really"]
        }
        
        words = text.split()
        filler_list = fillers.get(language, fillers["en"])
        
        for _ in range(n):
            if len(words) == 0:
                break
            
            insert_pos = random.randint(0, len(words))
            filler = random.choice(filler_list)
            words.insert(insert_pos, filler)
        
        return " ".join(words)
    
    def random_deletion(self, text: str, p: float = 0.1) -> str:
        """
        Randomly delete words with probability p.
        
        Args:
            text: Input text
            p: Probability of deleting each word
            
        Returns:
            Augmented text
        """
        words = text.split()
        
        # Keep at least 1 word
        if len(words) == 1:
            return text
        
        new_words = [word for word in words if random.random() > p]
        
        # If all words deleted, keep one random word
        if len(new_words) == 0:
            new_words = [random.choice(words)]
        
        return " ".join(new_words)
    
    def random_swap(self, text: str, n: int = 1) -> str:
        """
        Randomly swap positions of n pairs of words.
        
        Args:
            text: Input text
            n: Number of swaps
            
        Returns:
            Augmented text
        """
        words = text.split()
        
        if len(words) < 2:
            return text
        
        for _ in range(n):
            idx1 = random.randint(0, len(words) - 1)
            idx2 = random.randint(0, len(words) - 1)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return " ".join(words)
    
    def augment(self, text: str, language: str = "vi", num_augments: int = 3) -> List[str]:
        """
        Generate multiple augmented versions of text.
        
        Args:
            text: Input text
            language: "vi" or "en"
            num_augments: Number of augmented samples to generate
            
        Returns:
            List of augmented texts
        """
        augmented_texts = []
        
        for _ in range(num_augments):
            # Randomly select augmentation technique
            technique = random.choice([
                'synonym', 'insertion', 'deletion', 'swap', 'combined'
            ])
            
            aug_text = text
            
            if technique == 'synonym':
                aug_text = self.synonym_replacement(aug_text, language, n=random.randint(1, 2))
            elif technique == 'insertion':
                aug_text = self.random_insertion(aug_text, language, n=random.randint(1, 2))
            elif technique == 'deletion':
                aug_text = self.random_deletion(aug_text, p=0.1)
            elif technique == 'swap':
                aug_text = self.random_swap(aug_text, n=1)
            else:  # combined
                aug_text = self.synonym_replacement(aug_text, language, n=1)
                aug_text = self.random_insertion(aug_text, language, n=1)
            
            # Only add if different from original
            if aug_text != text:
                augmented_texts.append(aug_text)
        
        return augmented_texts


def augment_dataset(input_path: str, output_path: str, target_size: int = 1000):
    """
    Augment dataset to reach target size.
    
    Args:
        input_path: Path to original dataset JSON
        output_path: Path to save augmented dataset
        target_size: Target number of samples after augmentation
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📁 Original dataset size: {len(data)}")
    
    augmentor = TextAugmentor()
    augmented_data = data.copy()
    
    while len(augmented_data) < target_size:
        # Randomly select sample to augment
        original = random.choice(data)
        
        # Detect language (simple heuristic)
        language = "vi" if any(c in original['text'] for c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ") else "en"
        
        # Generate augmented versions
        aug_texts = augmentor.augment(original['text'], language, num_augments=1)
        
        for aug_text in aug_texts:
            # Create augmented sample
            aug_sample = original.copy()
            aug_sample['text'] = aug_text
            aug_sample['augmented'] = True
            augmented_data.append(aug_sample)
            
            if len(augmented_data) >= target_size:
                break
    
    # Save augmented dataset
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(augmented_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Augmented dataset saved: {len(augmented_data)} samples")
    print(f"   Output: {output_path}")


if __name__ == "__main__":
    # Example: augment existing dataset
    augment_dataset(
        input_path="ml/training/nlp_dataset.json",
        output_path="ml/training/nlp_dataset_augmented.json",
        target_size=500
    )
