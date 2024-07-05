import os
from ebooklib import epub
from bs4 import BeautifulSoup

# Read the HTML file
html_file_path = '2.html'
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Create a new EPUB book
book = epub.EpubBook()

# Set metadata
book.set_identifier('id123456')
book.set_title('Sample Book')
book.set_language('en')

book.add_author('Author Name')

# Define CSS style and extract images
style = """
body { font-family: Arial, Helvetica, sans-serif; }
.rect-0 { position: absolute; left: 39px; top: 100px; width: 822px; height: 438px; background-size: cover; }
.text-1 { position: absolute; left: 57px; top: 576px; width: 108.61px; height: 36.16px; font-size: 32px; font-family: 'fjalla one'; color: #000000; }
.text-2 { position: absolute; left: 49px; top: 637.96px; width: 563.5px; height: 39.05px; font-size: 16px; font-family: 'arial'; color: black; }
.text-3 { position: absolute; left: 61px; top: 756.96px; width: 216.5px; height: 458.51px; font-size: 16px; font-family: 'arial'; color: black; }
.text-4 { position: absolute; left: 347px; top: 754.96px; width: 216.5px; height: 458.51px; font-size: 16px; font-family: 'arial'; color: black; }
.text-5 { position: absolute; left: 626px; top: 752.96px; width: 216.5px; height: 458.51px; font-size: 16px; font-family: 'arial'; color: black; }
"""

# Add images
image_paths = {
    'children.png': 'children.png',
    'animal.png': 'animal.png'
}

for img_name, img_path in image_paths.items():
    with open(img_path, 'rb') as img_file:
        img_content = img_file.read()
        epub_image = epub.EpubItem(uid=img_name, file_name=img_name, media_type='image/png', content=img_content)
        book.add_item(epub_image)
        # Update the CSS with the EPUB image path
        style += f".image-{list(image_paths.keys()).index(img_name) + 6} {{ position: absolute; background-image: url({img_name}); background-size: cover; }}\n"

# Add the style to the book
nav_css = epub.EpubItem(uid='style_nav', file_name='style/nav.css', media_type='text/css', content=style)
book.add_item(nav_css)

# Create an introduction section
intro = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='en')
intro.content = '<h1>Introduction</h1><p>This is the introduction.</p>'
book.add_item(intro)

# Extract the body content from the HTML
body_content = soup.body.decode_contents()
main_section = epub.EpubHtml(title='Main Content', file_name='main_content.xhtml', lang='en')
main_section.content = f"<html><head><link rel='stylesheet' type='text/css' href='style/nav.css' /></head><body>{body_content}</body></html>"
book.add_item(main_section)


# Define Table of Contents
book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
            epub.Link('main_content.xhtml', 'Main Content', 'main_content'))

# Add default NCX and Nav files
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Create spine
book.spine = ['nav', intro, main_section]

# Write to the file
output_path = 'sample_book.epub'
epub.write_epub(output_path, book, {})

print(f"EPUB file has been created: {output_path}")
