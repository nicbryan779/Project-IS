import matplotlib
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import cv2
import os
from keras import backend as K
from pyimagesearch.resnet import ResnetBuilder


def dataTraining():
	#switch for labels
	def label_switch(x):
		return {
	        'burger': 0,
	        'pizza': 1,
			'sushi': 2,
			'icecream': 3,
			'pasta': 4,
			'sate': 5,
	    }[x]

	#settings for training
	EPOCHS = 25
	INIT_LR = 1e-3
	BS = 64

	# initialize the data and labels
	print("[INFO] loading images...")
	data = []
	labels = []

	# grab the image paths and randomly shuffle them
	imagePaths = sorted(list(paths.list_images("images")))
	random.seed(42)
	random.shuffle(imagePaths)

	# loop over the input images
	for imagePath in imagePaths:
		# load the image, pre-process it, and store it in the data list
		image = cv2.imread(imagePath)
		print(imagePath)
		image = cv2.resize(image, (128, 128))
		image = img_to_array(image)
		data.append(image)

		# extract the class label from the image path and update the
		# labels list
		label = imagePath.split(os.path.sep)[-2]
		label = label_switch(label)
		labels.append(label)

	# scale the raw pixel intensities to the range [0, 1]
	data = np.array(data, dtype="float") / 255.0
	labels = np.array(labels)

	# partition the data into training and testing splits using 75% of
	# the data for training and the remaining 25% for testing
	(trainX, testX, trainY, testY) = train_test_split(data,
		labels, test_size=0.25, random_state=42)

	# convert the labels from integers to vectors
	trainY = to_categorical(trainY, num_classes=6)
	testY = to_categorical(testY, num_classes=6)

	# construct the image generator for data augmentation
	aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
		height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
		horizontal_flip=True, fill_mode="nearest")

	# initialize the model
	print("[INFO] compiling resnet model...")
	# model = LeNet.build(width=128, height=128, depth=3, classes=6
	model = ResnetBuilder.build_resnet_18((3,128,128),6)
	opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
	model.compile(loss="binary_crossentropy", optimizer=opt,
		metrics=["accuracy"])

	# train the networks
	print("[INFO] training network...")
	H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
		validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
		epochs=EPOCHS, verbose=1)

	# save the model to disk
	print("[INFO] serializing network...")
	model.save("resnetfood.model")

	# plot the training loss and accuracy
	plt.style.use("ggplot")
	plt.figure()
	N = EPOCHS
	plt.plot(np.arange(0, N), H.history["loss"], label="train_loss+")
	plt.plot(np.arange(0, N), H.history["val_loss"], label="val_loss")
	plt.plot(np.arange(0, N), H.history["acc"], label="train_acc")
	plt.plot(np.arange(0, N), H.history["val_acc"], label="val_acc")
	plt.title("Training Loss and Accuracy on Food")
	plt.xlabel("Epoch #")
	plt.ylabel("Loss/Accuracy")
	plt.legend(loc="lower left")
	plt.savefig("")

	return "Training Success"
