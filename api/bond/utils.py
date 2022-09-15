def remove_white_spaces(serials):
    serials = serials.split(",")
    serials = list(map(str.strip, serials))
    while ("" in serials):
        serials.remove("")
    return serials
