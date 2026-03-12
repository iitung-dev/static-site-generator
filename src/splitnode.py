from textnode import TextType, TextNode
from extractmarkdownimageslinks import extract_markdown_images, extract_markdown_links

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for node in old_nodes:
        # 1. As-is check: Only process TEXT nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # 2. Split the string by the delimiter
        parts = node.text.split(delimiter)

        # 3. Validation: If length is even, a delimiter was left open
        if len(parts) % 2 == 0:
            raise Exception(f"Invalid Markdown: Delimiter {delimiter} not closed.")
        
        # 4. Create new nodes from the parts
        split_nodes = []
        for i in range(len(parts)):
            if parts[i] == "":
                continue
            
            # Even indices (0, 2, 4...) are outside the delimiters
            if i % 2 == 0:
                split_nodes.append(TextNode(parts[i], TextType.TEXT))
            # Odd indices (1, 3, 5...) are inside the delimiters
            else:
                split_nodes.append(TextNode(parts[i], text_type))
        
        new_nodes.extend(split_nodes)
        
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        original_text = node.text
        images = extract_markdown_images(original_text)
        
        if len(images) == 0:
            new_nodes.append(node)
            continue
            
        for image in images:
            image_alt = image[0]
            image_url = image[1]
            # Split the text into two parts: before the image and after the image
            sections = original_text.split(f"![{image_alt}]({image_url})", 1)
            
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not found")
            
            # If there is text before the image, add it as a TEXT node
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                
            # Add the IMAGE node
            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_url))
            
            # The remaining text to be processed
            original_text = sections[1]
            
        # After the loop, if there's any text left, add it
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
            
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        original_text = node.text
        links = extract_markdown_links(original_text)
        
        if len(links) == 0:
            new_nodes.append(node)
            continue
            
        for link in links:
            link_text = link[0]
            link_url = link[1]
            sections = original_text.split(f"[{link_text}]({link_url})", 1)
            
            if len(sections) != 2:
                raise ValueError("Invalid markdown, link section not found")
            
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            original_text = sections[1]
            
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
            
    return new_nodes

def text_to_textnodes(text):
    # Start with a list containing one big text node
    nodes = [TextNode(text, TextType.TEXT)]
    
    # 1. Handle Bold
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    # 2. Handle Italics
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    # 3. Handle Code
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    # 4. Handle Images
    nodes = split_nodes_image(nodes)
    # 5. Handle Links
    nodes = split_nodes_link(nodes)
    
    return nodes