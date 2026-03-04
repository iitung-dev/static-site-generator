from textnode import TextType, TextNode

def main():
    newTextNode = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(newTextNode)

main()