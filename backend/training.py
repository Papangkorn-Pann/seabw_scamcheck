import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import kagglehub
import os

print("=" * 60)
print("SCAMCHECK - BERT Model Fine-Tuning (Thai call dataset + SEA sms dataset)")
print("=" * 60)

# Download Thai call center dataset
print("\nDownloading Thai call center dataset...")
thai_path = kagglehub.dataset_download("jxxn03x/thai-call-center-call-log-dataset")
print("Path to Thai dataset:", thai_path)

# Download SMS Spam Collection dataset
print("\nDownloading SMS Spam Collection dataset...")
sms_path = kagglehub.dataset_download("uciml/sms-spam-collection-dataset")
print("Path to SMS Spam dataset:", sms_path)

# Load Thai call center dataset
print("\n" + "=" * 60)
print("Loading Thai call center dataset...")
print("=" * 60)
thai_files = [f for f in os.listdir(thai_path) if f.endswith('.csv')]
if thai_files:
    thai_file_path = os.path.join(thai_path, thai_files[0])
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    thai_df = None
    for encoding in encodings:
        try:
            thai_df = pd.read_csv(thai_file_path, encoding=encoding)
            print(f"Successfully loaded with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue

    if thai_df is not None:
        print(f"Thai dataset shape: {thai_df.shape}")
        print(f"Columns: {thai_df.columns.tolist()}")
    else:
        print("Could not load Thai dataset!")
        thai_df = pd.DataFrame()
else:
    print("No CSV files found in Thai dataset!")
    thai_df = pd.DataFrame()

# Load SMS Spam Collection dataset
print("\n" + "=" * 60)
print("Loading SMS Spam Collection dataset...")
print("=" * 60)
sms_files = [f for f in os.listdir(sms_path) if f.endswith('.csv')]
if sms_files:
    sms_file_path = os.path.join(sms_path, sms_files[0])
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    sms_df = None
    for encoding in encodings:
        try:
            sms_df = pd.read_csv(sms_file_path, encoding=encoding)
            print(f"Successfully loaded with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue

    if sms_df is not None:
        print(f"SMS Spam dataset shape: {sms_df.shape}")
        print(f"Columns: {sms_df.columns.tolist()}")
    else:
        print("Could not load SMS dataset!")
        sms_df = pd.DataFrame()
else:
    print("No CSV files found in SMS Spam dataset!")
    sms_df = pd.DataFrame()

# Prepare Thai dataset
print("\n" + "=" * 60)
print("Preparing Thai call center dataset...")
print("=" * 60)
if not thai_df.empty:
    thai_df_clean = thai_df[['Text', 'Type']].copy()
    thai_df_clean.columns = ['text', 'label']

    # Convert to binary: Scam=1, Everything else=0
    thai_df_clean['labels'] = (thai_df_clean['label'] == 'Scam').astype(int)
    thai_df_clean = thai_df_clean[['text', 'labels']].dropna()

    print(f"Thai unique labels (binary): {sorted(thai_df_clean['labels'].unique())}")
    print(f"Thai label distribution: Scam={sum(thai_df_clean['labels'])}, Not-Scam={len(thai_df_clean)-sum(thai_df_clean['labels'])}")
    print(f"Thai dataset prepared: {thai_df_clean.shape}")
else:
    thai_df_clean = pd.DataFrame(columns=['text', 'labels'])

# Prepare SMS Spam dataset
print("\n" + "=" * 60)
print("Preparing SMS Spam Collection dataset...")
print("=" * 60)
if not sms_df.empty:
    sms_df_clean = sms_df[['v1', 'v2']].copy()
    sms_df_clean.columns = ['label', 'text']

    unique_labels = sorted(sms_df_clean['label'].unique())
    print(f"SMS unique labels: {unique_labels}")
    label_map = {label: idx for idx, label in enumerate(unique_labels)}
    print(f"SMS label mapping: {label_map}")

    sms_df_clean['labels'] = sms_df_clean['label'].map(label_map)
    sms_df_clean = sms_df_clean[['text', 'labels']].dropna()

    print(f"SMS dataset prepared: {sms_df_clean.shape}")
else:
    sms_df_clean = pd.DataFrame(columns=['text', 'labels'])

# Combine datasets
print("\n" + "=" * 60)
print("Combining datasets...")
print("=" * 60)
df_clean = pd.concat([thai_df_clean, sms_df_clean], ignore_index=True)
df_clean['labels'] = df_clean['labels'].astype(int)

print(f"Combined dataset shape: {df_clean.shape}")
print(f"  - Thai call center: {len(thai_df_clean)} samples")
print(f"  - SMS Spam Collection: {len(sms_df_clean)} samples")

# Create Hugging Face dataset
dataset = Dataset.from_pandas(df_clean[['text', 'labels']])

# Split into train and validation (80-20 split)
split_dataset = dataset.train_test_split(test_size=0.2)
train_dataset = split_dataset['train']
eval_dataset = split_dataset['test']

print(f"\nTrain dataset size: {len(train_dataset)}")
print(f"Eval dataset size: {len(eval_dataset)}")

# Load Multilingual BERT tokenizer and model
print("\nLoading Multilingual BERT model and tokenizer...")
model_name = "bert-base-multilingual-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Set pad token for BERT
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Tokenize the datasets
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=128)

print("Tokenizing datasets...")
train_dataset = train_dataset.map(tokenize_function, batched=True)
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

# Remove text column after tokenization
train_dataset = train_dataset.remove_columns(['text'])
eval_dataset = eval_dataset.remove_columns(['text'])

# Set format for PyTorch
train_dataset.set_format("torch")
eval_dataset.set_format("torch")

# Set up training arguments
print("\nSetting up training configuration...")
training_args = TrainingArguments(
    output_dir="./scam_detector_bert",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

# Initialize Trainer
print("Initializing Trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Fine-tune the model
print("\n" + "=" * 60)
print("Starting BERT fine-tuning...")
print("=" * 60 + "\n")
trainer.train()

# Save the fine-tuned model
print("\n" + "=" * 60)
print("Fine-tuning complete! Saving model...")
print("=" * 60)
trainer.save_model("./scam_detector_bert_final")
tokenizer.save_pretrained("./scam_detector_bert_final")

print("\nModel saved to: ./scam_detector_bert_final")
print("You can now use this model for scam detection!")
