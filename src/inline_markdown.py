import re
from enum import Enum

from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


_HEADING_PATTERN = re.compile(r"^#{1,6} ")


def block_to_block_type(block):
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    first_line = block.split("\n", 1)[0]
    if _HEADING_PATTERN.match(first_line):
        return BlockType.HEADING

    lines = block.split("\n")

    if lines and all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if lines and all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if lines:
        expected = 1
        for line in lines:
            if not line.startswith(f"{expected}. "):
                break
            expected += 1
        else:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


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


def markdown_to_blocks(markdown):
    return [block.strip() for block in markdown.split("\n\n") if block.strip()]


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes


def text_to_children(text):
    return [text_node_to_html_node(n) for n in text_to_textnodes(text)]


def _collapse_whitespace(text):
    return " ".join(text.split())


def _paragraph_block_to_html_node(block):
    return ParentNode("p", text_to_children(_collapse_whitespace(block)))


def _heading_block_to_html_node(block):
    lines = block.split("\n")
    m = re.match(r"^(#{1,6}) (.*)$", lines[0])
    if not m:
        return _paragraph_block_to_html_node(block)
    level = len(m.group(1))
    tag = f"h{level}"
    parts = [m.group(2)]
    parts.extend(lines[1:])
    inner = _collapse_whitespace(" ".join(parts))
    return ParentNode(tag, text_to_children(inner))


def _code_block_to_html_node(block):
    body = block[4:-3]
    code_leaf = text_node_to_html_node(TextNode(body, TextType.TEXT))
    return ParentNode("pre", [ParentNode("code", [code_leaf])])


def _quote_block_to_html_node(block):
    stripped = []
    for line in block.split("\n"):
        rest = line[1:] if line.startswith(">") else line
        stripped.append(rest.lstrip())
    inner = _collapse_whitespace("\n".join(stripped))
    return ParentNode("blockquote", text_to_children(inner))


def _unordered_list_block_to_html_node(block):
    items = []
    for line in block.split("\n"):
        item_text = line[2:] if line.startswith("- ") else line
        items.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ul", items)


def _ordered_list_block_to_html_node(block):
    lines = block.split("\n")
    items = []
    for i, line in enumerate(lines):
        prefix = f"{i + 1}. "
        item_text = line[len(prefix) :] if line.startswith(prefix) else line
        items.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ol", items)


def _block_to_html_node(block):
    btype = block_to_block_type(block)
    match btype:
        case BlockType.PARAGRAPH:
            return _paragraph_block_to_html_node(block)
        case BlockType.HEADING:
            return _heading_block_to_html_node(block)
        case BlockType.CODE:
            return _code_block_to_html_node(block)
        case BlockType.QUOTE:
            return _quote_block_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return _unordered_list_block_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return _ordered_list_block_to_html_node(block)


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    if not blocks:
        return ParentNode("div", [text_node_to_html_node(TextNode("", TextType.TEXT))])
    children = [_block_to_html_node(block) for block in blocks]
    return ParentNode("div", children)
