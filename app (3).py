# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1l-YLGyDqmv4j2wJH-cmFtUIIzMTsQs1-
"""

import streamlit as st
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# Load model and tokenizers
@st.cache_resource
def load_model_and_tokenizers():
    model = tf.keras.models.load_model("Teacher_Model.keras", custom_objects=None)
    with open('encoder_tokenizer.pkl', 'rb') as f:
        encoder_tokenizer = pickle.load(f)
    with open('decoder_tokenizer.pkl', 'rb') as f:
        decoder_tokenizer = pickle.load(f)
    return model, encoder_tokenizer, decoder_tokenizer

model, encoder_tokenizer, decoder_tokenizer = load_model_and_tokenizers()

# Constants
START_TOKEN = '<start>'
END_TOKEN = '<end>'
start_token_id = decoder_tokenizer.word_index.get(START_TOKEN.strip('<>'))
end_token_id = decoder_tokenizer.word_index.get(END_TOKEN.strip('<>'))
max_input_len = 1600
max_output_len = 500
index_to_word = {v: k for k, v in decoder_tokenizer.word_index.items()}

# Summary generation logic
def generate_summary(text):
    input_seq = encoder_tokenizer.texts_to_sequences([text])
    input_seq = pad_sequences(input_seq, maxlen=max_input_len, padding='post')
    encoder_input = tf.convert_to_tensor(input_seq)

    encoder_output, enc_hidden, enc_cell = model.encoder(encoder_input)
    decoder_state = [enc_hidden, enc_cell]
    decoder_input = tf.expand_dims([start_token_id], 0)
    generated_ids = []

    for _ in range(max_output_len):
        predictions, hidden, cell = model.decoder(decoder_input, states=decoder_state)
        predicted_id = tf.argmax(predictions[0, -1, :]).numpy()
        if predicted_id == end_token_id:
            break
        generated_ids.append(predicted_id)
        decoder_input = tf.expand_dims([predicted_id], 0)
        decoder_state = [hidden, cell]

    summary_words = [index_to_word.get(id, '') for id in generated_ids]
    return ' '.join(summary_words)

# Streamlit App UI
st.set_page_config(page_title="Text Summarizer", layout="wide")
st.title("📰 Text Summarization App")
st.markdown("Enter a news article below, and the model will generate a summary.")

article_input = st.text_area("Enter article text:", height=300)

if st.button("Generate Summary"):
    if article_input.strip() == "":
        st.warning("Please enter some text before generating the summary.")
    else:
        with st.spinner("Generating summary..."):
            summary = generate_summary(article_input)
        st.subheader("Generated Summary")
        st.write(summary)