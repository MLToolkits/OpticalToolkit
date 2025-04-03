from typing import List

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def _convert_images_to_numpy(images: List[np.ndarray | list]) -> List[np.ndarray]:
    converted_images = []
    for img in images:
        if isinstance(img, list):
            img = np.array(img)
        if not isinstance(img, np.ndarray):
            raise TypeError(f"Images must be a list or NumPy array. Found {type(img)}.")
        converted_images.append(img)
    return converted_images


def _resize_images_to_largest(images: List[np.ndarray]) -> List[np.ndarray]:
    max_height = max(img.shape[0] for img in images)
    max_width = max(img.shape[1] for img in images)

    resized_images = []
    for img in images:
        pil_img = Image.fromarray(img.astype(np.uint8))
        resized_img = np.array(pil_img.resize((max_width, max_height), Image.BICUBIC))
        resized_images.append(resized_img)

    return resized_images


def _sort_images_by_targets(
    images: List[np.ndarray], targets: list
) -> List[np.ndarray]:
    sorted_images_targets = sorted(zip(images, targets), key=lambda x: x[1])
    sorted_images = [x[0] for x in sorted_images_targets]
    sorted_targets = [x[1] for x in sorted_images_targets]

    return sorted_images, sorted_targets


def _plot_and_save(
    images: List[np.ndarray], targets: list | None, cols: int, output_path: str
) -> plt.Figure:
    num_images = len(images)
    rows = (num_images + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))
    axes = axes.flatten()

    for i, (img, ax) in enumerate(zip(images, axes)):
        ax.imshow(img)
        ax.axis("off")
        if targets is not None:
            ax.set_title(str(targets[i]), fontsize=max(8, 12 - cols))

    for ax in axes[num_images:]:
        ax.set_visible(False)

    plt.subplots_adjust(wspace=0.2, hspace=0.4)

    plt.savefig(output_path, bbox_inches="tight")
    print(f"Plot saved to {output_path}")
    plt.show()

    return fig
