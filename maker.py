from ebooklib import epub
import json
import os
from urllib.parse import urlparse
import requests

def downloadResource(url):
    url = url.replace('localhost:8888/createbookstudio/site', 'createbookstudio.com')
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        path = urlparse(url).path
        file_name = os.path.basename(path)
        save_path = f'demo/{file_name}'
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved: {save_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        
    return save_path

def add_page(book, pageContent, pageName):
    # Example of parsing text and image positions from Fabric.js JSON
    elements = []
    rect_elements = []
    image_elements = []
    for obj in pageContent['objects']:
        if obj["type"] == 'rect':
            elements.append({
                'type': 'rect',
                'style': f"""
                        position: absolute;
                        left: {obj['left']}px;
                        top: {obj['top']}px;
                        width: {obj['width']}px;
                        height: {obj['height']}px;
                        overflow: hidden;
                    """
            })
        elif obj['type'] == 'group':
            if obj['clipPath']:
                rect_elements.append({
                    'type': 'svg',
                    'objects': obj['objects'],
                    'width': obj['width'],
                    'height': obj['height'],
                    'style': f"""
                        position: absolute;
                        left: {obj['left'] - obj['clipPath']['left']}px;
                        top: {obj['top'] - obj['clipPath']["top"]}px;
                    """
                })
            else :
                elements.append({
                    'type': 'svg',
                    'objects': obj['objects'],
                    'width': obj['width'],
                    'height': obj['height'],
                    'style': f"""
                            position: absolute;
                            left: {obj['left']}px;
                            top: {obj['top']}px;
                        """
                })
                
        elif obj['type'] == 'image':
            img_url = downloadResource(obj['src'])
            image_elements.append(img_url)
            if obj['clipPath']:
                rect_elements.append({
                    'type': 'image',
                    'src': img_url,
                    'style': f"""
                        position: absolute;
                        left: {obj['left'] - obj['clipPath']['left']}px;
                        top: {obj['top'] - obj['clipPath']["top"]}px;
                        width: {obj['width'] * obj['scaleX']}px;
                        height: {obj['height'] * obj['scaleY']}px;
                    """
                })
            else:
                elements.append({
                    'type': 'image',
                    'src': img_url,
                    'style': f"""
                        position: absolute;
                        left: {obj['left']}px;
                        top: {obj['top']}px;
                        width: {obj['width']}px;
                        height: {obj['height']}px;
                    """
            })
        elif (obj['type'] == 'text' or obj['type'] == 'textbox'):
            elements.append({
                'type': 'text',
                'text': obj['text'],
                'style': f"""
                    position: absolute;
                    font-family: {obj['fontFamily']};
                    font-size: {obj['fontSize']}px!important;
                    color: {obj['fill']};
                    left: {obj['left']}px;
                    top: {obj['top']}px;
                    width: {obj['width'] * obj['scaleX']}px;
                    height: {obj['height'] * obj['scaleY']}px;
                """
            })
       
    html_content = '<body>'

    # Add HTML for each element
    for elem in elements:
        if elem['type'] == 'rect':
            html_content += f'<div style="{elem["style"]}">' 
            for rect_elem in rect_elements:
                if rect_elem['type'] == 'image':
                    html_content += f'<img src="{rect_elem["src"]}" style="{rect_elem["style"]}"/>'
                if rect_elem['type'] == 'svg':
                    html_content += f'<svg height={rect_elem["height"]} width={rect_elem["width"]} style="{rect_elem["style"]}">'
                    for ele in rect_elem['objects']:
                        stroke = ele['stroke']
                        fill = ele['fill']
                        path_data = "M"
                        stroke_width = ele['strokeWidth'] if ele['strokeWidth'] > 0 else 1
                        for path in ele['path']:
                            idx = 0
                            if len(path) > 1:
                                for pt in path:
                                    if idx:
                                        path_data += f" {pt}"
                                    idx += 1
                        html_content += f'\n<path d="{path_data}" stroke={stroke} fill="{fill}" stroke-width="{stroke_width}" />'
                    html_content += '</svg>'
            html_content += f'</div>'
        elif elem['type'] == 'image':
            html_content += f'<img style="{elem["style"]}" src="{elem["src"]}"/>'
        elif elem['type'] == 'svg':
            html_content += f'<svg height={elem["height"]} width={elem["width"]} style="{elem["style"]}">'
            for ele in elem['objects']:
                stroke = ele['stroke']
                fill = ele['fill']
                path_data = "M"
                stroke_width = ele['strokeWidth'] if ele['strokeWidth'] > 0 else 1
                for path in ele['path']:
                    idx = 0
                    if len(path) > 1:
                        for pt in path:
                            if idx:
                                path_data += f" {pt}"
                            idx += 1
                html_content += f'\n<path d="{path_data}" stroke={stroke} fill="{fill}" stroke-width="{stroke_width}" />'
            html_content += '</svg>'
        elif elem['type'] == 'text':
            html_content += f'<div style="{elem["style"]}">{elem["text"]}</div>'

    html_content += '</body>'
    
    # Add page into Book
    page = epub.EpubHtml(title=f'Page {pageName}', file_name=f'page_{pageName}.xhtml', lang='en')
    page.content = html_content
    book.add_item(page)
    # Define Table Of Contents
    book.toc.append(page)

    return image_elements

def add_img(src):
    # create image from the local image
    imgSource = open(src, "rb").read()
    img = epub.EpubImage(
        uid="image_1",
        file_name=src,
        media_type="image/png",
        content=imgSource,
    )
    return img

def createEPub(json_url):
    # Load JSON data
    try:
        response = requests.get(json_url)
        response.raise_for_status()  # Check if the request was successful
        epub_data = json.loads(response.content)
    except Exception as e:
        print(f"Failed to load {json_url}: {e}")
    
    # Initialize the ePub book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id123456') #Change the id for you
    book.set_title('Sample Book')
    book.set_language('en')
    book.add_author('Author Marvin Elmore')

    # Create image_list
    image_list = []
    for pageData in epub_data["book_pages"]:
        page_content = json.loads(pageData["page_content"])
        image_list.extend(add_page(book, page_content, pageData["page_number"]))

    for img_path in image_list:
        book.add_item(add_img(img_path))

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS style
    style = 'body {position: relative;}'

    # Add CSS to the book
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Define CSS for all spine documents
    book.spine = ['nav'] + book.toc

    # Write to the file
    epub.write_epub('out/demo_book.epub', book, {})
    
createEPub('https://createbookstudio-2-fmh57.ondigitalocean.app/book/canvas-data/2/2')