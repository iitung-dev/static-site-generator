import unittest
from textnode import TextNode, TextType
from splitnode import split_nodes_delimiter, split_nodes_link, split_nodes_image

class TestSplitNodes(unittest.TestCase):
    def test_split_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[1].text, "bolded")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)

    def test_split_code(self):
        node = TextNode("This has `code` here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Just plain text")

    def test_multiple_nodes(self):
        node1 = TextNode("Node one `code`", TextType.TEXT)
        node2 = TextNode("Node two", TextType.BOLD) # Should be kept "as-is"
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[2].text_type, TextType.BOLD)

    def test_exception_raised(self):
        node = TextNode("This is **missing the end", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)


class TestSplitImagesLinks(unittest.TestCase):
    ## Image Tests
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
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_image_at_start(self):
        node = TextNode("![alt](url) leading text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "alt")
        self.assertEqual(new_nodes[0].text_type, TextType.IMAGE)

    ## Link Tests
    def test_split_links(self):
        node = TextNode(
            "Check [Boot.dev](https://www.boot.dev) and [Google](https://www.google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Check ", TextType.TEXT),
                TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("Google", TextType.LINK, "https://www.google.com"),
            ],
            new_nodes,
        )

    def test_split_link_at_end(self):
        node = TextNode("Text then [link](url)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)

    ## Edge Case Tests
    def test_no_links(self):
        node = TextNode("Just some plain text here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Just some plain text here")

    def test_preserve_other_types(self):
        # This tests that our "As-Is" logic works for images/links
        bold_node = TextNode("I am bold", TextType.BOLD)
        new_nodes = split_nodes_link([bold_node])
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)

if __name__ == "__main__":
    unittest.main()