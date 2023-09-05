import tensorflow as tf

model = tf.keras.models.load_model(
    "C:/Users/henry/Desktop/yolo-cppe5_1.tar.gz")

converter = tf.lite.TFLiteConverter.from_keras_model(model)

tflite_model = converter.convert()
open("yolo-cppe5_1.tflite", "wb").write(tflite_model)
