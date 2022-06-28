from typing import List, Protocol

from PIL.Image import Image


class Filter(Protocol):
    hide: bool

    def apply(self, image: Image) -> Image:
        ...


def evaluate_image(image: Image, filter_stack: List[Filter]):
    new_image = image
    for f in filter_stack:
        if not f.hide:
            new_image = f.apply(new_image)
    return new_image
