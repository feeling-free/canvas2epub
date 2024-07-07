import json

# Load JSON data
with open('json/sample_readable.json', 'r') as f:
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
                'style': f"""
                        position: absolute;
                        left: {obj['left']}px;
                        top: {obj['top']}px;
                        width: {obj['width']}px;
                        height: {obj['height']}px;
                        overflow: hidden;
                    """
            })
        elif obj['type'] == 'image':
            if obj['clipPath']:
                rect_elements.append({
                    'type': 'image',
                    'src': obj['src'],
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
                    'src': obj['src'],
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
                    font-size: {obj['fontSize']};
                    color: {obj['fill']};
                    left: {obj['left']}px;
                    top: {obj['top']}px;
                    width: {obj['width'] * obj['scaleX']}px;
                    height: {obj['height'] * obj['scaleY']}px;
                """
            })

    html_content = '<!DOCTYPE html><html><head><style>'
    html_content += 'body { position: relative; }'
    back_style = f"""
            position: absolute;
            left: {backImg['left']}px;
            top: {backImg['top']}px;
            width: {backImg['width']}px;
            height: {backImg['height']}px;
        """
        
    # Add background 
    html_content += f'</style></head><img src="{backImg["src"]}" style="{back_style}"/>'

    # Add HTML for each element
    for elem in elements:
        if elem['type'] == 'rect':
            html_content += f'<div style="{elem["style"]}">' 
            for rect_elem in rect_elements:
                if rect_elem['type'] == 'image':
                    html_content += f'<img src="{rect_elem["src"]}" style="{rect_elem["style"]}"/>'
            html_content += f'</div>'
        elif elem['type'] == 'image':
            html_content += f'<img style="{elem["style"]}" src="{elem["src"]}"/>'
        elif elem['type'] == 'text':
            html_content += f'<div style="{elem["style"]}">{elem["text"]}</div>'

    html_content += '</body></html>'

    # Save HTML content to a file
    with open(f'./html/{pageName}.html', 'w') as f:
        f.write(html_content)
        
for pageData in epub_data["book_pages"]:
    get_contents(pageData["page_content"], pageData["page_number"])
