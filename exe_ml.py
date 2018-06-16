import os
import pickle
import pandas as pd
import MeCab
import neologdn
from sys import exit
from sklearn.linear_model import Ridge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error


tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
tagger.parse(' ')


def read_df():

    f = sorted(os.listdir("data"), reverse=True)[0]
    df = pd.read_csv("data/" + f)

    return df


def to_corpus(docs):

    word_classes = ['名詞','動詞','形容詞','形容動詞','副詞','連体詞']

    input = neologdn.normalize(docs)
    output = ""

    node = tagger.parseToNode(input)

    while node:
        feature = node.feature.split(",")
        if feature[0] in word_classes:
            output += str(node.surface) + " "
        node = node.next

    return output


def load_stop_word():

    with open("stop_words.txt", "r") as f:
        stop_words = [w.strip("\n") for w in f]

    return stop_words


def nlp(df):

    X, y = df['corpus'].values, df['point'].values
    stop_words = load_stop_word()
    vectorizer = TfidfVectorizer(min_df=3, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b', stop_words=stop_words, ngram_range=(1, 3))
    X_vecs = vectorizer.fit_transform(X)

    try:
        os.mkdir("models")
    except:
        pass

    with open("models/vectorizer.pickle", "wb") as f:
        pickle.dump(vectorizer, f)

    return X_vecs, y


def ml_exe(df, pipe, param_grid, ml_name):

    X_vecs, y = nlp(df)
    X_train, X_test, y_train, y_test = train_test_split(X_vecs, y, random_state=0)

    grid = GridSearchCV(pipe, param_grid, cv=5)
    grid.fit(X_train, y_train)

    with open("models/" + ml_name +"_model.pickle", "wb") as f:
        pickle.dump(grid.best_estimator_.named_steps[ml_name], f)

    y_pred = grid.best_estimator_.predict(X_test)

    try:
        os.mkdir("log")
    except:
        pass

    with open("log/result_" + ml_name + ".txt", "w") as file:
        print("Mean Absolute Error: {:.3f}".format(mean_absolute_error(y_test, y_pred)), file=file)
        print("Best Parameters:\n{}".format(grid.best_params_), file=file)


if __name__ == '__main__':

    df = read_df()
    df = df.dropna().reset_index(drop=True)
    df['corpus'] = [to_corpus(str(docs)) for docs in df['docs'].values]

    param_grid = {'ridge__alpha': [10**x for x in range(-5, 5)],
              'ridge__fit_intercept': [True, False],
              'ridge__normalize': [True, False],
              'ridge__random_state': [0]
              }

    pipe = make_pipeline(Ridge())

    ml_exe(df, pipe, param_grid, "ridge")
