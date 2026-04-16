import unittest

from inline_markdown import (
    BlockType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestExtractMarkdownImages(unittest.TestCase):
    def test_two_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(
            extract_markdown_images(text),
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )

    def test_single_image(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_no_images(self):
        self.assertEqual(extract_markdown_images("plain text"), [])

    def test_does_not_match_plain_links(self):
        self.assertEqual(extract_markdown_images("[link](https://example.com)"), [])


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_two_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(
            extract_markdown_links(text),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        )

    def test_no_links(self):
        self.assertEqual(extract_markdown_links("plain text"), [])

    def test_does_not_match_images(self):
        self.assertEqual(
            extract_markdown_links("![alt](https://example.com/img.png)"), []
        )


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_delimiter_example(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold_delimiter(self):
        node = TextNode(
            "This is text with a **bolded phrase** in the middle", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_italic_single_underscore(self):
        node = TextNode("Some _italic_ words here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Some ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" words here", TextType.TEXT),
            ],
        )

    def test_no_delimiter_in_text(self):
        node = TextNode("plain text only", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("plain text only", TextType.TEXT)])

    def test_multiple_pairs_same_string(self):
        node = TextNode("a **b** c **d** e", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" c ", TextType.TEXT),
                TextNode("d", TextType.BOLD),
                TextNode(" e", TextType.TEXT),
            ],
        )

    def test_non_text_nodes_pass_through_unchanged(self):
        bold = TextNode("already bold", TextType.BOLD)
        text = TextNode("plain **split** me", TextType.TEXT)
        link = TextNode("link", TextType.LINK, "https://example.com")
        new_nodes = split_nodes_delimiter([bold, text, link], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("plain ", TextType.TEXT),
                TextNode("split", TextType.BOLD),
                TextNode(" me", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_empty_delimited_segment(self):
        node = TextNode("before `` after", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("", TextType.CODE),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_unclosed_delimiter_raises(self):
        node = TextNode("only `open", TextType.TEXT)
        with self.assertRaises(ValueError) as ctx:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("closing delimiter", str(ctx.exception).lower())

    def test_unclosed_bold_raises(self):
        node = TextNode("start **no end", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_odd_number_of_delimiters_raises(self):
        node = TextNode("**a** extra **", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_preserves_url_on_text_nodes(self):
        node = TextNode("a `b` c", TextType.TEXT, "https://ignored-for-text")
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        for n in new_nodes:
            self.assertEqual(n.url, "https://ignored-for-text")

    def test_does_not_split_inside_non_text_types(self):
        """Underscores inside BOLD are left as literal (no nested inline)."""
        nodes = [
            TextNode("before ", TextType.TEXT),
            TextNode("_not_italic_", TextType.BOLD),
            TextNode(" after", TextType.TEXT),
        ]
        out = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual(out, nodes)

    def test_chained_code_then_bold_on_plain_text_segments(self):
        node = TextNode("say `x` then **y**", TextType.TEXT)
        after_code = split_nodes_delimiter([node], "`", TextType.CODE)
        after_bold = split_nodes_delimiter(after_code, "**", TextType.BOLD)
        self.assertEqual(
            after_bold,
            [
                TextNode("say ", TextType.TEXT),
                TextNode("x", TextType.CODE),
                TextNode(" then ", TextType.TEXT),
                TextNode("y", TextType.BOLD),
                TextNode("", TextType.TEXT),
            ],
        )


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_single_image_at_start(self):
        node = TextNode(
            "![lead](https://example.com/a.png) trailing words", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("lead", TextType.IMAGE, "https://example.com/a.png"),
                TextNode(" trailing words", TextType.TEXT),
            ],
        )

    def test_single_image_at_end(self):
        node = TextNode(
            "prefix text ![pic](https://cdn.example.org/x.jpg)", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("prefix text ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://cdn.example.org/x.jpg"),
            ],
        )

    def test_entire_string_is_one_image(self):
        node = TextNode("![solo](https://img.dev/1.gif)", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node]),
            [TextNode("solo", TextType.IMAGE, "https://img.dev/1.gif")],
        )

    def test_no_images_returns_original_text_node(self):
        node = TextNode("plain text with [a link](https://x.com) only", TextType.TEXT)
        out = split_nodes_image([node])
        self.assertEqual(out, [node])
        self.assertIs(out[0], node)

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [node])

    def test_empty_alt_text(self):
        node = TextNode("see ![](https://placeholder/empty.png) here", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("see ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://placeholder/empty.png"),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_adjacent_images_no_text_between(self):
        node = TextNode(
            "x ![a](https://a.com/1)![b](https://b.com/2) y", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("x ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://a.com/1"),
                TextNode("b", TextType.IMAGE, "https://b.com/2"),
                TextNode(" y", TextType.TEXT),
            ],
        )

    def test_three_images(self):
        node = TextNode(
            "![one](https://o/1) mid ![two](https://t/2) ![three](https://th/3)",
            TextType.TEXT,
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("one", TextType.IMAGE, "https://o/1"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("two", TextType.IMAGE, "https://t/2"),
                TextNode(" ", TextType.TEXT),
                TextNode("three", TextType.IMAGE, "https://th/3"),
            ],
        )

    def test_preserves_parent_url_on_text_segments(self):
        node = TextNode(
            "a ![i](https://x.com/z.png) b",
            TextType.TEXT,
            "https://parent-context",
        )
        out = split_nodes_image([node])
        self.assertEqual(
            out,
            [
                TextNode("a ", TextType.TEXT, "https://parent-context"),
                TextNode("i", TextType.IMAGE, "https://x.com/z.png"),
                TextNode(" b", TextType.TEXT, "https://parent-context"),
            ],
        )

    def test_non_text_nodes_pass_through_unchanged(self):
        bold = TextNode("![fake](https://not-parsed)", TextType.BOLD)
        text = TextNode("real ![ok](https://yes.png) end", TextType.TEXT)
        link = TextNode("cap", TextType.LINK, "https://example.com")
        out = split_nodes_image([bold, text, link])
        self.assertEqual(
            out,
            [
                TextNode("![fake](https://not-parsed)", TextType.BOLD),
                TextNode("real ", TextType.TEXT),
                TextNode("ok", TextType.IMAGE, "https://yes.png"),
                TextNode(" end", TextType.TEXT),
                TextNode("cap", TextType.LINK, "https://example.com"),
            ],
        )

    def test_does_not_split_inside_non_text_types(self):
        nodes = [
            TextNode("before ", TextType.TEXT),
            TextNode("![in bold](https://ignored.png)", TextType.BOLD),
            TextNode(" after", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_image(nodes), nodes)

    def test_empty_input_list(self):
        self.assertEqual(split_nodes_image([]), [])

    def test_url_with_query_and_fragment(self):
        node = TextNode(
            "x ![q](https://cdn/img.png?w=10#frag) y", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("x ", TextType.TEXT),
                TextNode("q", TextType.IMAGE, "https://cdn/img.png?w=10#frag"),
                TextNode(" y", TextType.TEXT),
            ],
        )

    def test_nested_brackets_in_alt_no_match_entire_string_unchanged(self):
        """Nested `[` in alt breaks the image pattern; nothing is split."""
        node = TextNode(r"![a[b]](https://u.com)", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [node])


class TestSplitNodesLink(unittest.TestCase):
    def test_two_links_assignment_example(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
        )

    def test_single_link_at_start(self):
        node = TextNode("[first](https://a.com) rest of line", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("first", TextType.LINK, "https://a.com"),
                TextNode(" rest of line", TextType.TEXT),
            ],
        )

    def test_single_link_at_end(self):
        node = TextNode("intro [tail](https://tail.io/)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("intro ", TextType.TEXT),
                TextNode("tail", TextType.LINK, "https://tail.io/"),
            ],
        )

    def test_entire_string_is_one_link(self):
        node = TextNode("[only](https://only.org)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [TextNode("only", TextType.LINK, "https://only.org")],
        )

    def test_no_links_returns_original_node(self):
        node = TextNode("no brackets here", TextType.TEXT)
        out = split_nodes_link([node])
        self.assertEqual(out, [node])
        self.assertIs(out[0], node)

    def test_images_are_not_links(self):
        node = TextNode(
            "text ![alt](https://img.png) and [real](https://link.org)", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("text ![alt](https://img.png) and ", TextType.TEXT),
                TextNode("real", TextType.LINK, "https://link.org"),
            ],
        )

    def test_empty_link_label(self):
        node = TextNode("empty [](https://empty.label/) now", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("empty ", TextType.TEXT),
                TextNode("", TextType.LINK, "https://empty.label/"),
                TextNode(" now", TextType.TEXT),
            ],
        )

    def test_adjacent_links(self):
        node = TextNode("[a](https://a)[b](https://b)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("a", TextType.LINK, "https://a"),
                TextNode("b", TextType.LINK, "https://b"),
            ],
        )

    def test_preserves_parent_url_on_text_segments(self):
        node = TextNode(
            "see [doc](https://docs.io) end",
            TextType.TEXT,
            "https://ctx",
        )
        out = split_nodes_link([node])
        self.assertEqual(
            out,
            [
                TextNode("see ", TextType.TEXT, "https://ctx"),
                TextNode("doc", TextType.LINK, "https://docs.io"),
                TextNode(" end", TextType.TEXT, "https://ctx"),
            ],
        )

    def test_non_text_nodes_pass_through(self):
        img = TextNode("![x](https://y)", TextType.IMAGE)
        text = TextNode("go [here](https://z) ok", TextType.TEXT)
        code = TextNode("`code`", TextType.CODE)
        out = split_nodes_link([img, text, code])
        self.assertEqual(
            out,
            [
                TextNode("![x](https://y)", TextType.IMAGE),
                TextNode("go ", TextType.TEXT),
                TextNode("here", TextType.LINK, "https://z"),
                TextNode(" ok", TextType.TEXT),
                TextNode("`code`", TextType.CODE),
            ],
        )

    def test_does_not_split_inside_bold(self):
        nodes = [
            TextNode("a ", TextType.TEXT),
            TextNode("[not a link](https://nope)", TextType.BOLD),
            TextNode(" b", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_link(nodes), nodes)

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        self.assertEqual(split_nodes_link([node]), [node])

    def test_empty_input_list(self):
        self.assertEqual(split_nodes_link([]), [])

    def test_multiple_links_with_trailing_text(self):
        node = TextNode(
            "[one](https://1.com) between [two](https://2.com) tail", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("one", TextType.LINK, "https://1.com"),
                TextNode(" between ", TextType.TEXT),
                TextNode("two", TextType.LINK, "https://2.com"),
                TextNode(" tail", TextType.TEXT),
            ],
        )

    def test_url_with_at_sign_and_path(self):
        node = TextNode(
            "ch [vid](https://www.youtube.com/@bootdotdev/videos) done", TextType.TEXT
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("ch ", TextType.TEXT),
                TextNode("vid", TextType.LINK, "https://www.youtube.com/@bootdotdev/videos"),
                TextNode(" done", TextType.TEXT),
            ],
        )

    def test_chained_split_link_then_image_on_segments(self):
        """After links are extracted, image splitter can run on remaining TEXT."""
        node = TextNode(
            "![i](https://img.com/x.png) then [l](https://l.org)", TextType.TEXT
        )
        after_link = split_nodes_link([node])
        after_both = split_nodes_image(after_link)
        self.assertEqual(
            after_both,
            [
                TextNode("i", TextType.IMAGE, "https://img.com/x.png"),
                TextNode(" then ", TextType.TEXT),
                TextNode("l", TextType.LINK, "https://l.org"),
            ],
        )

    def test_nested_brackets_in_label_no_match_entire_string_unchanged(self):
        node = TextNode(r"[a[b]](https://u.com)", TextType.TEXT)
        self.assertEqual(split_nodes_link([node]), [node])


class TestTextToTextnodes(unittest.TestCase):
    def test_assignment_example(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )

    def test_plain_text_only(self):
        self.assertEqual(
            text_to_textnodes("hello world"),
            [TextNode("hello world", TextType.TEXT)],
        )

    def test_empty_string(self):
        self.assertEqual(text_to_textnodes(""), [TextNode("", TextType.TEXT)])

    def test_bold_only(self):
        self.assertEqual(
            text_to_textnodes("**x**"),
            [
                TextNode("", TextType.TEXT),
                TextNode("x", TextType.BOLD),
                TextNode("", TextType.TEXT),
            ],
        )

    def test_image_before_link_in_same_string(self):
        self.assertEqual(
            text_to_textnodes("![a](https://img) [b](https://lnk)"),
            [
                TextNode("a", TextType.IMAGE, "https://img"),
                TextNode(" ", TextType.TEXT),
                TextNode("b", TextType.LINK, "https://lnk"),
            ],
        )

    def test_code_before_bold_so_backticks_protect_asterisks(self):
        self.assertEqual(
            text_to_textnodes(r"`not **bold**` **is**"),
            [
                TextNode("", TextType.TEXT),
                TextNode(r"not **bold**", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("is", TextType.BOLD),
                TextNode("", TextType.TEXT),
            ],
        )

    def test_link_url_not_parsed_for_inline_markdown(self):
        """Delimiters in URL are not in TEXT nodes after link split."""
        self.assertEqual(
            text_to_textnodes("[x](https://ex.com/_y_)"),
            [TextNode("x", TextType.LINK, "https://ex.com/_y_")],
        )

    def test_chained_inline_without_images_or_links(self):
        self.assertEqual(
            text_to_textnodes("**b** _i_ `c`"),
            [
                TextNode("", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("i", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("c", TextType.CODE),
                TextNode("", TextType.TEXT),
            ],
        )

    def test_unclosed_bold_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("**no close")


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_empty_and_whitespace_only(self):
        self.assertEqual(markdown_to_blocks(""), [])
        self.assertEqual(markdown_to_blocks("   \n\n  \n  "), [])

    def test_strips_blocks_and_drops_extra_blank_lines(self):
        md = "\n\n# Heading\n\n\nPara one.\n\n\n\nPara two.\n"
        self.assertEqual(
            markdown_to_blocks(md),
            ["# Heading", "Para one.", "Para two."],
        )

    def test_single_block_no_double_newline(self):
        self.assertEqual(markdown_to_blocks("one line"), ["one line"])


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph_plain(self):
        self.assertEqual(block_to_block_type("Hello world."), BlockType.PARAGRAPH)

    def test_paragraph_when_no_space_after_hashes(self):
        self.assertEqual(block_to_block_type("#not-a-heading"), BlockType.PARAGRAPH)

    def test_paragraph_when_too_many_hashes(self):
        self.assertEqual(
            block_to_block_type("####### seven hashes is not a heading"),
            BlockType.PARAGRAPH,
        )

    def test_heading_levels_one_through_six(self):
        for n in range(1, 7):
            hashes = "#" * n
            self.assertEqual(
                block_to_block_type(f"{hashes} Title text"),
                BlockType.HEADING,
                msg=f"level {n}",
            )

    def test_code_block_empty_body(self):
        self.assertEqual(block_to_block_type("```\n```"), BlockType.CODE)

    def test_code_block_with_content(self):
        block = "```\nline1\nline2\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_not_code_without_newline_after_opening_fence(self):
        self.assertEqual(block_to_block_type("```inline```"), BlockType.PARAGRAPH)

    def test_not_code_without_closing_fence(self):
        self.assertEqual(block_to_block_type("```\nno close"), BlockType.PARAGRAPH)

    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type("> quoted"), BlockType.QUOTE)

    def test_quote_space_after_gt_optional(self):
        self.assertEqual(block_to_block_type(">tight\n> loose"), BlockType.QUOTE)

    def test_quote_multiline(self):
        block = "> first\n> second\n> third"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_not_quote_if_any_line_missing_gt(self):
        self.assertEqual(
            block_to_block_type("> one\nnot quoted"),
            BlockType.PARAGRAPH,
        )

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- a\n- b\n- c"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_not_unordered_without_space_after_hyphen(self):
        self.assertEqual(block_to_block_type("-no space"), BlockType.PARAGRAPH)

    def test_ordered_list_single_line(self):
        self.assertEqual(block_to_block_type("1. first"), BlockType.ORDERED_LIST)

    def test_ordered_list_increments(self):
        block = "1. a\n2. b\n3. c"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_not_ordered_when_not_starting_at_one(self):
        self.assertEqual(block_to_block_type("2. wrong"), BlockType.PARAGRAPH)

    def test_not_ordered_when_sequence_breaks(self):
        self.assertEqual(
            block_to_block_type("1. a\n3. skipped"),
            BlockType.PARAGRAPH,
        )

    def test_empty_block_is_paragraph(self):
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)

    def test_markdown_to_blocks_then_block_types(self):
        md = """# Title

A paragraph.

```
code
```

> quote

- u1
- u2

1. o1
2. o2
"""
        blocks = markdown_to_blocks(md)
        types = [block_to_block_type(b) for b in blocks]
        self.assertEqual(
            types,
            [
                BlockType.HEADING,
                BlockType.PARAGRAPH,
                BlockType.CODE,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
            ],
        )


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading_levels(self):
        md = "# One\n\n## Two\n\n###### Six"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h1>One</h1><h2>Two</h2><h6>Six</h6></div>",
        )

    def test_blockquote(self):
        md = "> line **one**\n> line two"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote><p>line <b>one</b> line two</p></blockquote></div>",
        )

    def test_unordered_list(self):
        md = "- **a**\n- b"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><b>a</b></li><li>b</li></ul></div>",
        )

    def test_ordered_list(self):
        md = "1. first\n2. second"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>first</li><li>second</li></ol></div>",
        )

    def test_empty_document(self):
        node = markdown_to_html_node("")
        self.assertEqual(node.to_html(), "<div></div>")


if __name__ == "__main__":
    unittest.main()
