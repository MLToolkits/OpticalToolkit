from tensorflow import keras
import numpy as np
import tensorflow as tf
import random


def display_filters(model_path, layer_name=None):
    model = instantiate_model(model_path)
    layer = get_layer(model, layer_name)

    feature_extractor = keras.Model(inputs=model.input, outputs=layer.output)

    def compute_loss(image, filter_index):
        activation = feature_extractor(image)
        filter_activation = activation[:, 2:-2, 2:-2, filter_index]
        return tf.reduce_mean(filter_activation)

    @tf.function
    def gradient_ascent_step(image, filter_index, learning_rate):
        with tf.GradientTape() as tape:
            tape.watch(image)
            loss = compute_loss(image, filter_index)
        grads = tape.gradient(loss, image)
        grads = tf.math.l2_normalize(grads)
        image += learning_rate * grads
        return image

    img_width = 200
    img_height = 200

    def generate_filter_pattern(filter_index):
        iterations = 30
        learning_rate = 10.0
        image = tf.random.uniform(
            minval=0.4, maxval=0.6, shape=(1, img_width, img_height, 3)
        )
        for i in range(iterations):
            image = gradient_ascent_step(image, filter_index, learning_rate)
        return image[0].numpy()

    all_images = []

    for filter_index in range(64):
        print(f"Processing filter {filter_index}")
        filter_index = tf.convert_to_tensor(filter_index, dtype=tf.int32)
        image = deprocess_image(generate_filter_pattern(filter_index))
        all_images.append(image)

    margin = 5
    n = 8
    cropped_width = img_width - 25 * 2
    cropped_height = img_height - 25 * 2
    width = n * cropped_width + (n - 1) * margin
    height = n * cropped_height + (n - 1) * margin
    stitched_filters = np.zeros((width, height, 3))

    for i in range(n):
        for j in range(n):
            image = all_images[i * n + j]
            stitched_filters[
                (cropped_width + margin) * i: (cropped_width + margin) * i
                + cropped_width,
                (cropped_height + margin) * j: (cropped_height + margin) * j
                + cropped_height,
                :,
            ] = image

    keras.utils.save_img(
        f"filters_for_layer_{layer_name}.png", stitched_filters)


def instantiate_model(model_path):
    try:
        model = tf.keras.load_model(model_path)
    except ValueError as e:
        raise ValueError(f"{e}: Model not found")
    else:
        model = tf.keras.applications.xception.Xception(
            weights="imagenet", include_top=False
        )

    return model


def get_layer(model, layer_name):
    if layer_name is None:
        # Find all convolutional layers in the model
        conv_layers = [
            layer for layer in model.layers if isinstance(layer, keras.layers.Conv2D)
        ]

        if not conv_layers:
            raise ValueError("No convolutional layers found in the model.")

        layer = random.choice(conv_layers)
        layer_name = layer.name  # Update layer_name to the chosen layer's name
    else:
        layer = model.get_layer(name=layer_name)

    return layer


def deprocess_image(image):
    image -= image.mean()
    image /= image.std()
    image *= 64
    image += 128
    image = np.clip(image, 0, 255).astype("uint8")
    image = image[25:-25, 25:-25, :]
    return image
