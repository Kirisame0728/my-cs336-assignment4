import fasttext

def classify_nsfw(text):
    model = fasttext.load_model("data/classifiers/jigsaw_fasttext_bigrams_nsfw_final.bin")
    label, score = model.predict(text.replace('\n', ' '))
    label = label[0].replace('__label__', '')
    score = score[0]
    return label, score

def classify_toxic_speech(text):
    model = fasttext.load_model("data/classifiers/jigsaw_fasttext_bigrams_hatespeech_final.bin")
    label, score = model.predict(text.replace('\n', ' '))
    label = label[0].replace('__label__', '')
    score = score[0]
    return label, score
