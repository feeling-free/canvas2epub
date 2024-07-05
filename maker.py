from ebooklib import epub


with open('2.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Step 3: Create EPUB file
book = epub.EpubBook()
book.set_identifier('id123456')
book.set_title('Sample Book')
book.set_language('en')

chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
chapter.content = html_content
book.add_item(chapter)

book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap_01'),)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

style = 'body { font-family: Arial, sans-serif; }'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

book.spine = ['nav', chapter]

epub.write_epub('example_book.epub', book, {})