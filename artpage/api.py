import os

import frappe
from PIL import Image, ImageOps


@frappe.whitelist()
def rotate_artwork_image(artwork):
    """Rotate an Artwork's existing image 90 degrees clockwise, in place."""
    if not frappe.has_permission("Artwork", "write", doc=artwork):
        frappe.throw("You are not permitted to edit this artwork.", frappe.PermissionError)

    image_url = frappe.db.get_value("Artwork", artwork, "image")
    if not image_url:
        frappe.throw("This artwork has no image to rotate.")

    file_doc = frappe.get_doc("File", {"file_url": image_url})
    file_path = file_doc.get_full_path()

    with Image.open(file_path) as img:
        # Normalize any embedded EXIF orientation first, so a rotation we
        # apply here isn't re-applied on top by EXIF-aware viewers/browsers.
        img = ImageOps.exif_transpose(img)
        rotated = img.rotate(-90, expand=True)
        rotated.save(file_path)

    frappe.db.set_value("File", file_doc.name, "file_size", os.path.getsize(file_path))

    return {"image_url": image_url}
