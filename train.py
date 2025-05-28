import json
import numpy as np
import pickle
import random
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()

# Load intents
with open('intents.json') as file:
    data = json.load(file)

sentences = []
labels = []
label_list = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        sentences.append(pattern.lower())
        labels.append(intent['tag'])
    if intent['tag'] not in label_list:
        label_list.append(intent['tag'])

# Encode labels
le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

# Save label encoder
with open('labelencoder.pickle', 'wb') as f:
    pickle.dump(le, f)

# Tokenize input sentences
tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(sentences)
sequences = tokenizer.texts_to_sequences(sentences)
padded_sequences = pad_sequences(sequences, padding='post')

# Save tokenizer
with open('tokenizer.pickle', 'wb') as f:
    pickle.dump(tokenizer, f)

# Build model
model = Sequential([
    Embedding(1000, 16, input_length=padded_sequences.shape[1]),
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dense(len(label_list), activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()

# Train model
model.fit(padded_sequences, labels_encoded, epochs=200)

# Save model
model.save('bankchatbot_model.h5')
print("Training complete. Model saved as 'bankchatbot_model.h5'.")
