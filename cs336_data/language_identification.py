import fasttext

def identify_lang(text):
    model = fasttext.load_model('data/classifiers/lid.176.bin')
    lang, score = model.predict(text.replace('\n', ' '))
    lang = lang[0].replace('__label__', '')
    return lang, score[0]