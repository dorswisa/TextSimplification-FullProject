import pandas as pd
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from sklearn.utils import class_weight
from tensorflow import keras
import numpy as np
from keras.layers import Dense, Conv1D, Conv2D, Flatten, Dropout, MaxPooling1D
from keras.models import load_model
from sklearn import preprocessing

df = pd.read_csv('vectorsDataset.csv')

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

dataset = df.values

X = dataset[:, 0:304]
Y = dataset[:, 304]

min_max_scaler = preprocessing.MinMaxScaler()
X_scale = min_max_scaler.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(X_scale, Y, test_size=0.3, random_state=20)


# model = Sequential()
# model.add(Conv1D(32, kernel_size=3, activation='relu', input_shape=(304,1)))
# model.add(Conv1D(64, kernel_size=3, activation='relu'))
# model.add(Flatten())
# model.add(Dense(1, activation='sigmoid'))
# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#
# hist = model.fit(X_train, y_train,
#           batch_size=128, epochs=200, class_weight={0: 0.08, 1: 0.92})



model = load_model('200epc,128batch_model.h5')

print(model.evaluate(X_test, y_test)[1])
print(model.predict(X_scale[1100:1200]))

prediction = model.predict(X_scale)

summary = np.where(prediction > 0.5)

Ysummary = np.where(Y == 1)

np.intersect1d(summary, Ysummary)
