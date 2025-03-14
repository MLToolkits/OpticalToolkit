import tensorflow as tf

from optical_toolkit.utils.deprocess_image import deprocess_image


def compute_loss(image, filter_index, feature_extractor):
    activation = feature_extractor(image)
    filter_activation = activation[:, 2:-2, 2:-2, filter_index]
    return tf.reduce_mean(filter_activation)


@tf.function
def gradient_ascent_step(image, filter_index, learning_rate, feature_extractor):
    with tf.GradientTape() as tape:
        tape.watch(image)
        loss = compute_loss(image, filter_index, feature_extractor)
    grads = tape.gradient(loss, image)
    grads = tf.math.l2_normalize(grads)
    image += learning_rate * grads
    return image


def generate_filter_pattern(filter_index, img_sz, feature_extractor):
    iterations = 30
    learning_rate = 10.0
    image = tf.random.uniform(minval=0.4, maxval=0.6, shape=(1, img_sz, img_sz, 3))
    for i in range(iterations):
        image = gradient_ascent_step(
            image, filter_index, learning_rate, feature_extractor
        )
    return image[0].numpy()


def generate_filter_patterns(layer, num_filters, img_sz, feature_extractor):
    all_images = []

    if layer.filters < num_filters:
        num_filters = layer.filters
        num_filters = max(num_filters, 64)

    for filter_index in range(num_filters):
        print(f"Processing filter {filter_index}")
        filter_index = tf.convert_to_tensor(filter_index, dtype=tf.int32)
        image = deprocess_image(
            generate_filter_pattern(filter_index, img_sz, feature_extractor)
        )
        all_images.append(image)

    return all_images


__all__ = [generate_filter_patterns]
