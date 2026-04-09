from textnode import TextNode, TextType


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
