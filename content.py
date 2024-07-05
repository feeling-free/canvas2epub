import json

# Load JSON data
with open('2_readable.json', 'r') as f:
    epub_data = json.load(f)

def get_contents(pageContent, pageName):
    # background image
    backImg = pageContent['backgroundImage']
    # Example of parsing text and image positions from Fabric.js JSON
    elements = []
    rect_elements = []
    for obj in pageContent['objects']:
        if obj["type"] == 'rect':
            elements.append({
                'type': 'rect',
                'left': obj['left'],
                'top': obj['top'],
                'width': obj['width'],
                'height': obj['height'],
                'fill': obj['fill']
            })
        elif obj['type'] == 'group':
            if obj['clipPath']:
                rect_elements.append({
                    'type': 'group',
                    'src': obj['src'],
                    'left': obj['left'] - obj['clipPath']["left"],
                    'top': obj['top'] - obj['clipPath']["top"],
                    'width': obj['width'] * obj['scaleX'],
                    'height': obj['height'] * obj['scaleY']
                })
            else:
                elements.append({
                    'type': 'group',
                    'src': obj['src'],
                    'left': obj['left'],
                    'top': obj['top'],
                    'width': obj['width'] * obj['scaleX'],
                    'height': obj['height'] * obj['scaleY']
            })
        elif obj['type'] == 'image':
            if obj['clipPath']:
                rect_elements.append({
                    'type': 'image',
                    'src': obj['src'],
                    'left': obj['left'] - obj['clipPath']["left"],
                    'top': obj['top'] - obj['clipPath']["top"],
                    'width': obj['width'] * obj['scaleX'],
                    'height': obj['height'] * obj['scaleY']
                })
            else:
                elements.append({
                    'type': 'image',
                    'src': obj['src'],
                    'left': obj['left'],
                    'top': obj['top'],
                    'width': obj['width'] * obj['scaleX'],
                    'height': obj['height'] * obj['scaleY']
            })
        elif (obj['type'] == 'text' or obj['type'] == 'textbox'):
            elements.append({
                'type': 'text',
                'text': obj['text'],
                'left': obj['left'],
                'top': obj['top'],
                'fontSize': obj['fontSize'],
                'fontFamily': obj['fontFamily'],
                'width': obj['width'] * obj['scaleX'],
                'height': obj['height'] * obj['scaleY'],
                'color': obj['fill']
            })

    print(elements)

    html_content = '<!DOCTYPE html><html><head><style>'
    html_content += 'body { position: relative; }'
    html_content += f"""
        .background {{
            position: absolute;
            left: {backImg['left']}px;
            top: {backImg['top']}px;
            width: {backImg['width']}px;
            height: {backImg['height']}px;
            background-size: cover;
            background-image: url('{backImg['src']}');
        }}
        """

    # Add CSS for each element
    for elem in elements:
        if elem['type'] == 'rect':
            html_content += f"""
            .rect-{elements.index(elem)} {{
                position: absolute;
                left: {elem['left']}px;
                top: {elem['top']}px;
                width: {elem['width']}px;
                height: {elem['height']}px;
                background-size: cover;
                overflow: hidden;
            }}
            """
            for rect_elem in rect_elements:
                if rect_elem['type'] == 'image':
                    html_content += f"""
                        .rect-image-{rect_elements.index(rect_elem)} {{
                            position: absolute;
                            left: {rect_elem['left']}px;
                            top: {rect_elem['top']}px;
                            width: {rect_elem['width']}px;
                            height: {rect_elem['height']}px;
                            background-image: url('{rect_elem['src']}');
                            background-size: cover;
                        }}
                        """
        elif elem['type'] == 'image':
            html_content += f"""
            .image-{elements.index(elem)} {{
                position: absolute;
                left: {elem['left']}px;
                top: {elem['top']}px;
                width: {elem['width']}px;
                height: {elem['height']}px;
                background-image: url('{elem['src']}');
                background-size: cover;
            }}
            """
        elif elem['type'] == 'text':
            html_content += f"""
            .text-{elements.index(elem)} {{
                position: absolute;
                left: {elem['left']}px;
                top: {elem['top']}px;
                width: {elem['width']}px;
                height: {elem['height']}px;
                font-size: {elem['fontSize']}px;
                font-family: '{elem['fontFamily']}';
                color: {elem['color']};
            }}
            """

    html_content += '</style></head><body>'

    # Add background 
    html_content += f'<div class="background"></div>'
    # Add HTML for each element
    for elem in elements:
        if elem['type'] == 'rect':
            html_content += f'<div class="rect-{elements.index(elem)}">' 
            for rect_elem in rect_elements:
                if rect_elem['type'] == 'image':
                    html_content += f'<div class="rect-image-{rect_elements.index(rect_elem)}"></div>'
            html_content += f'</div>'
        elif elem['type'] == 'image':
            html_content += f'<div class="image-{elements.index(elem)}"></div>'
        elif elem['type'] == 'text':
            html_content += f'<div class="text-{elements.index(elem)}">{elem["text"]}</div>'

    html_content += '</body></html>'

    # Save HTML content to a file
    with open(f'./html/{pageName}.html', 'w') as f:
        f.write(html_content)
        
for pageData in epub_data["book_pages"]:
    get_contents(pageData["page_content"], pageData["page_number"])
