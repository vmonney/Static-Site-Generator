import re

from textnode import TextNode, TextType


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        parts = old_node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(
                f"invalid Markdown: no matching closing delimiter {delimiter!r} in {old_node.text!r}"
            )
        for i, part in enumerate(parts):
            node_type = TextType.TEXT if i % 2 == 0 else text_type
            new_nodes.append(TextNode(part, node_type, old_node.url))
    return new_nodes


_LINK_PATTERN = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")
_IMAGE_PATTERN = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")


def _split_nodes_link_or_image(old_nodes, pattern, special_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        text = old_node.text
        last_end = 0
        found = False
        for m in pattern.finditer(text):
            found = True
            if m.start() > last_end:
                new_nodes.append(
                    TextNode(text[last_end : m.start()], TextType.TEXT, old_node.url)
                )
            new_nodes.append(TextNode(m.group(1), special_type, m.group(2)))
            last_end = m.end()
        if not found:
            new_nodes.append(old_node)
            continue
        if last_end < len(text):
            new_nodes.append(TextNode(text[last_end:], TextType.TEXT, old_node.url))
    return new_nodes


def split_nodes_image(old_nodes):
    return _split_nodes_link_or_image(old_nodes, _IMAGE_PATTERN, TextType.IMAGE)


def split_nodes_link(old_nodes):
    return _split_nodes_link_or_image(old_nodes, _LINK_PATTERN, TextType.LINK)


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes
