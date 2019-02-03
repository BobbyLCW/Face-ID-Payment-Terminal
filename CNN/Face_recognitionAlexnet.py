from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers.convolutional import ZeroPadding2D
from keras.preprocessing.image import img_to_array, load_img
from keras import backend as K
import numpy as np
import tensorflow as tf
import os
np.random.seed(1000)
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]=""

# dimensions of our images.
img_width, img_height = 224, 224
filepath = 'BobbyAWAlexnet.h5'
train_data_dir = 'data/train'
validation_data_dir = 'data/validation'
nb_train_samples = 2000
nb_validation_samples = 600
epochs = 15
batch_size = 25
number_of_class = 2

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

model = Sequential()
#1st layers
model.add(Conv2D(filters=96, kernel_size=(11, 11), activation='relu', input_shape=input_shape, strides=(4,4), padding = 'valid'))
model.add(MaxPooling2D(pool_size=(2, 2),strides=(2,2), padding = 'valid'))

#2nd layers
model.add(Conv2D(filters=256, kernel_size=(11, 11), activation='relu', strides=(1,1), padding = 'valid'))
model.add(MaxPooling2D(pool_size=(2, 2),strides=(2,2), padding = 'valid'))

#3rd layers
model.add(Conv2D(filters=384, kernel_size=(3, 3), activation='relu', strides=(1,1), padding = 'valid'))

#4th layers
model.add(Conv2D(filters=384, kernel_size=(3, 3), activation='relu', strides=(1,1), padding = 'valid'))

#5th layers
model.add(Conv2D(filters=256, kernel_size=(3, 3), activation='relu', strides=(1,1), padding = 'valid'))
model.add(MaxPooling2D(pool_size=(2, 2),strides=(2,2), padding = 'valid'))

model.add(Flatten())
model.add(Dense(4096, activation='relu', input_shape=(224*224*3,)))
model.add(Dropout(0.4))
model.add(Dense(4096, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(1000, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(number_of_class, activation='softmax'))
model.summary()
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# this is the augmentation configuration we will use for training
train_datagen = ImageDataGenerator(rescale=1. / 255, rotation_range=20,
                               width_shift_range=0.1,
                               height_shift_range=0.1,
                               shear_range=0.01,
                               horizontal_flip=True,
                               vertical_flip=True,
                               brightness_range=[0.5, 1.5])

# this is the augmentation configuration we will use for testing:
# only rescaling
test_datagen = ImageDataGenerator(rescale=1. / 255, rotation_range=20,
                               width_shift_range=0.1,
                               height_shift_range=0.1,
                               shear_range=0.01,
                               horizontal_flip=True,
                               vertical_flip=True,
                               brightness_range=[0.5, 1.5])

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')
	
print("\nvalidation: ")
print(validation_generator.class_indices)
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
# check 5 epochs
early_stop = EarlyStopping(monitor='val_acc', patience=5, mode='max') 
callbacks_list = [checkpoint, early_stop]

model.fit_generator(
    train_generator,
    steps_per_epoch=nb_train_samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples // batch_size,
    callbacks=callbacks_list,
    shuffle=True)
model.save(filepath)