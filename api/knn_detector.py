import os
import pickle
from PIL import Image, ImageDraw
import face_recognition
from datetime import datetime
from sklearn import neighbors
from django.conf import settings

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ROOT_DIR = "/Users/mavericktena/Pictures/"

def image_files_in_folder(folder):
    """Return a list of image file paths in a folder"""
    return [os.path.join(folder, f) for f in os.listdir(folder) if
            os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]


def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []

    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(
                        face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)

    n_neighbors = n_neighbors or int(round(math.sqrt(len(X))))
    if verbose:
        print("Chose n_neighbors automatically:", n_neighbors)

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    if model_save_path:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.6):
    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if not knn_clf and not model_path:
        raise Exception("Must supply knn classifier either through knn_clf or model_path")

    if not knn_clf:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    if len(X_face_locations) == 0:
        return []

    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    predictions = [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in
                   zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]
    return predictions


def show_prediction_labels_on_image(img_path, predictions):
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
        name = name.encode("UTF-8")
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    del draw

    filename = "Labeled_{0}.png".format(datetime.now().strftime("%Y%m%d%H%M%S"))
    pil_image.save(settings.MEDIA_ROOT + "/labeled/" + filename)
    return filename


if __name__ == "__main__":
    print("Training KNN classifier...")
    classifier = train("train_dir/", model_save_path="trained_knn_model.clf", n_neighbors=10)
    print("Training complete!")
