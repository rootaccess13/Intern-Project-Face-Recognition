from . knn_detector import *
import os


def train_model():
    print("Training KNN classifier...")
    classifier = knn_detector.train("train_dir/", model_save_path="trained_knn_model_2.clf", n_neighbors=10)
    print("Training complete!")

    return classifier

train_model()  