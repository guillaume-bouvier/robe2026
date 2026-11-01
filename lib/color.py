def rgb(r, g, b):
    """Convert RGB values to a tuple."""
    return (r, g, b)


def hex_to_rgb(hex_color):
    """Convert a hex color to an RGB tuple."""
    return ((hex_color >> 16) & 0xFF, (hex_color >> 8) & 0xFF, hex_color & 0xFF)
