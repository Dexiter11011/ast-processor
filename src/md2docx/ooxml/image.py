"""OOXML inline image builder."""

from __future__ import annotations

import struct
from lxml import etree

from md2docx.ooxml.paragraph import build_paragraph
from md2docx.ooxml.run import build_run
from md2docx.ooxml.text import build_text
from md2docx.ooxml.xml_builder import R_NS, W_NS, w_element, w_tag

WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"

EMU_PER_INCH = 914_400
EMU_PER_PIXEL = 9_525
DEFAULT_WIDTH_EMU = 4 * EMU_PER_INCH


def read_image_dimensions(data: bytes) -> tuple[int, int]:
    """Return pixel width and height for PNG/JPEG payloads."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        if width and height:
            return width, height
    if data.startswith(b"\xff\xd8\xff"):
        return _jpeg_dimensions(data)
    return 96, 96


def _jpeg_dimensions(data: bytes) -> tuple[int, int]:
    index = 2
    while index < len(data) - 8:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[index + 3 : index + 7])
            if width and height:
                return width, height
            break
        if marker in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9):
            continue
        segment_length = struct.unpack(">H", data[index : index + 2])[0]
        index += segment_length
    return 96, 96


def scale_to_max_width(width_px: int, height_px: int, *, max_width_emu: int = DEFAULT_WIDTH_EMU) -> tuple[int, int]:
    width_emu = width_px * EMU_PER_PIXEL
    height_emu = height_px * EMU_PER_PIXEL
    if width_emu <= max_width_emu:
        return width_emu, height_emu
    scale = max_width_emu / width_emu
    return max_width_emu, int(height_emu * scale)


def build_image_paragraph(*, rel_id: str, width_emu: int, height_emu: int, doc_pr_id: int, name: str) -> etree._Element:
    """Build a paragraph containing an inline picture."""
    drawing = etree.Element(
        w_tag("drawing"),
        nsmap={
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "wp": WP_NS,
            "a": A_NS,
            "pic": PIC_NS,
            "r": R_NS,
        },
    )
    inline = etree.SubElement(
        drawing,
        f"{{{WP_NS}}}inline",
        {
            "distT": "0",
            "distB": "0",
            "distL": "0",
            "distR": "0",
        },
    )
    extent = etree.SubElement(inline, f"{{{WP_NS}}}extent")
    extent.set("cx", str(width_emu))
    extent.set("cy", str(height_emu))
    etree.SubElement(inline, f"{{{WP_NS}}}effectExtent", {"l": "0", "t": "0", "r": "0", "b": "0"})
    doc_pr = etree.SubElement(inline, f"{{{WP_NS}}}docPr")
    doc_pr.set("id", str(doc_pr_id))
    doc_pr.set("name", name)
    frame_pr = etree.SubElement(inline, f"{{{WP_NS}}}cNvGraphicFramePr")
    etree.SubElement(frame_pr, f"{{{A_NS}}}graphicFrameLocks", {"noChangeAspect": "1"})

    graphic = etree.SubElement(inline, f"{{{A_NS}}}graphic")
    graphic_data = etree.SubElement(
        graphic,
        f"{{{A_NS}}}graphicData",
        {"uri": "http://schemas.openxmlformats.org/drawingml/2006/picture"},
    )
    pic = etree.SubElement(graphic_data, f"{{{PIC_NS}}}pic")
    nv_pic_pr = etree.SubElement(pic, f"{{{PIC_NS}}}nvPicPr")
    etree.SubElement(nv_pic_pr, f"{{{PIC_NS}}}cNvPr", {"id": "0", "name": ""})
    etree.SubElement(nv_pic_pr, f"{{{PIC_NS}}}cNvPicPr")

    blip_fill = etree.SubElement(pic, f"{{{PIC_NS}}}blipFill")
    blip = etree.SubElement(blip_fill, f"{{{A_NS}}}blip")
    blip.set(f"{{{R_NS}}}embed", rel_id)
    stretch = etree.SubElement(blip_fill, f"{{{A_NS}}}stretch")
    etree.SubElement(stretch, f"{{{A_NS}}}fillRect")

    sp_pr = etree.SubElement(pic, f"{{{PIC_NS}}}spPr")
    xfrm = etree.SubElement(sp_pr, f"{{{A_NS}}}xfrm")
    etree.SubElement(xfrm, f"{{{A_NS}}}off", {"x": "0", "y": "0"})
    ext = etree.SubElement(xfrm, f"{{{A_NS}}}ext")
    ext.set("cx", str(width_emu))
    ext.set("cy", str(height_emu))
    prst_geom = etree.SubElement(sp_pr, f"{{{A_NS}}}prstGeom", {"prst": "rect"})
    etree.SubElement(prst_geom, f"{{{A_NS}}}avLst")

    run = w_element("r")
    run.append(drawing)
    return build_paragraph([run])


def build_alt_text_paragraph(alt: str) -> etree._Element:
    return build_paragraph([build_run([build_text(alt)])])
