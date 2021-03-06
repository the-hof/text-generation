import numpy as np

import argparse

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

def get_text_from_file(filename, seq_length):
    # load ascii text and covert to lowercase
    raw_text = open(filename).read()
    raw_text = raw_text.lower()
    # create mapping of unique chars to integers
    chars = sorted(list(set(raw_text)))
    char_to_int = dict((c, i) for i, c in enumerate(chars))
    # summarize the loaded data
    n_chars = len(raw_text)
    n_vocab = len(chars)
    print ("Total Characters: ", n_chars)
    print ("Total Vocab: ", n_vocab)
    # prepare the dataset of input to output pairs encoded as integers
    dataX = []
    dataY = []
    for i in range(0, n_chars - seq_length, 1):
        seq_in = raw_text[i:i + seq_length]
        seq_out = raw_text[i + seq_length]
        dataX.append([char_to_int[char] for char in seq_in])
        dataY.append(char_to_int[seq_out])
    n_patterns = len(dataX)
    print ("Total Patterns: ", n_patterns)

    # reshape X to be [samples, time steps, features]
    X = np.reshape(dataX, (n_patterns, seq_length, 1))
    # normalize
    X = X / float(n_vocab)
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)

    raw_text_data = (dataX, n_vocab, chars)

    return X,y,raw_text_data

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", help="location of text data to use as input")
parser.add_argument("-l", "--length", help="length of text strings to process", default="100")
parser.add_argument("-e", "--epochs", help="number of epochs to train model", default="50")
parser.add_argument("-m", "--model", help="location of pretrained model")
args = parser.parse_args()

X, y, raw_text_data = get_text_from_file(args.data, int(args.length))


def generate_text_from_model(model, raw_text_data):
    int_to_char = dict((i, c) for i, c in enumerate(raw_text_data[2]))
    start = np.random.randint(0, len(raw_text_data[0]) - 1)
    pattern = raw_text_data[0][start]
    print "Seed:"
    print "\"", ''.join([int_to_char[value] for value in pattern]), "\""
    # generate characters
    output = ""
    for i in range(1000):
        x = np.reshape(pattern, (1, len(pattern), 1))
        x = x / float(raw_text_data[1])
        prediction = model.predict(x, verbose=0)
        index = np.argmax(prediction)
        result = int_to_char[index]
        seq_in = [int_to_char[value] for value in pattern]
        output = output + result
        pattern.append(index)
        pattern = pattern[1:len(pattern)]

# define the LSTM model
model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(256))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))
if args.model:
    model.load_weights(args.model)
model.compile(loss='categorical_crossentropy', optimizer='adam')
# define the checkpoint
filepath="models/weights-%s-%s-{epoch:02d}-{loss:.4f}-bigger.hdf5" % (args.data.replace(".txt", ""), args.length)
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]
# fit the model
model.fit(X, y, epochs=int(args.epochs), batch_size=64, callbacks=callbacks_list)