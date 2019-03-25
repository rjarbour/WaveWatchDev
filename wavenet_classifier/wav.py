import pydub
from WaveNetClassifier import WaveNetClassifier
import numpy as np
import pandas as pd
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)

def get_model_memory_usage(batch_size, model):
    import numpy as np
    from keras import backend as K

    shapes_mem_count = 0
    for l in model.layers:
        single_layer_mem = 1
        for s in l.output_shape:
            if s is None:
                continue
            single_layer_mem *= s
        shapes_mem_count += single_layer_mem

    trainable_count = np.sum([K.count_params(p) for p in set(model.trainable_weights)])
    non_trainable_count = np.sum([K.count_params(p) for p in set(model.non_trainable_weights)])

    number_size = 4.0
    if K.floatx() == 'float16':
         number_size = 2.0
    if K.floatx() == 'float64':
         number_size = 8.0

    total_memory = number_size*(batch_size*shapes_mem_count + trainable_count + non_trainable_count)
    gbytes = np.round(total_memory / (1024.0 ** 3), 3)
    return gbytes

"""
wnc = WaveNetClassifier((19200,), (6,), kernel_size = 2, dilation_depth = 15, n_filters = 12, task = 'classification')
print(get_model_memory_usage(1, wnc.model))
exit(0)
"""

srate = 9600
xtrain, ytrain = [], []
xtest, ytest = [], []
c = [0,0,0,0,0,0]
meta = pd.read_csv("meta/esc50.csv")
meta["labels"] = meta.category.apply(
    lambda x: { 'clock_alarm': 1, 'car_horn': 2, 'siren': 3}.get(x, 5))
meta = meta.drop(meta[meta["labels"] == 5][:-200].index)
feat_list = np.array([])
feat_label = np.array([])
for index, row in meta.iterrows():
    try:
        sound = pydub.AudioSegment.from_wav("audio/{0}".format(row.filename))
        sound = sound.set_channels(1)
    except:
        raise IOError('Give me an audio  file which I can read!!')

    if sound.frame_rate != srate:
        sound = sound.set_frame_rate(srate)

    indexer = np.arange(19200)[None, :] + 1500 * np.arange(20)[:, None]
    sound = sound.raw_data
    sound = np.frombuffer(sound, dtype=np.int16)
    sound = sound[indexer]
    meme, dank = False, False
    for idx in sound:
        t = []
        if np.any(idx) or not dank:
            if not np.any(idx):
                xtrain.append(idx)
                for e in range(6):
                    if e == 5:
                        c[e] += 1
                        t.append(1.0)
                    else:
                        t.append(0.0)
                ytrain.append(t)
                dank = True
            elif not meme:
                xtest.append(idx)
                for e in range(6):
                    if e == row.labels:
                        c[e] += 1
                        t.append(1.0)
                    else:
                        t.append(0.0)
                ytest.append(t)
                meme = True
            else:
                xtrain.append(idx)
                for e in range(6):
                    if e == row.labels:
                        c[e] += 1
                        t.append(1.0)
                    else:
                        t.append(0.0)
                ytrain.append(t)


print(c)

xtrain, ytrain, xtest, ytest = np.array(xtrain), np.array(ytrain), np.array(xtest), np.array(ytest)
print(xtrain.shape)
print(xtest.shape)
wnc = WaveNetClassifier((19200,), (6,), kernel_size = 2, dilation_depth = 14, n_filters = 20, task = 'classification', load=True, load_dir="trained_wave.h5")
wnc.fit(xtrain, ytrain, validation_data = (xtest, ytest), epochs = 100, batch_size = 48, optimizer='adam', save=True, save_dir='./')

y_pred = wnc.predict(xtest)
