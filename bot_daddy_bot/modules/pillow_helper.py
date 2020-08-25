def get_size_by_one_side(image, width: int = None, height: int = None):
    if width and not height:
        diff_percent = width / image.width * 100
        height_percent = image.height * 0.01
        height = diff_percent * height_percent
    elif height and not width:
        diff_percent = height / image.height * 100
        width_percent = image.width * 0.01
        width = diff_percent * width_percent

    return int(width), int(height)


def get_size_by_one_side_not_specified(image, side: int):
    if image.width > image.height:
        new_width = side
        diff_percent = new_width / image.width * 100
        height_percent = image.height * 0.01
        new_height = diff_percent * height_percent
    else:
        new_height = side
        diff_percent = new_height / image.height * 100
        width_percent = image.width * 0.01
        new_width = diff_percent * width_percent

    return int(new_width), int(new_height)

