import json
import os
from urllib.parse import urlparse
import requests

# Load JSON data
with open('json/2_readable.json', 'r') as f:
    epub_data = json.load(f)

def get_default_font_name(s):
    # Split the string into words
    words = s.split()

    # Capitalize the first letter of each word
    case_words = [words[0].capitalize()] + [word.capitalize() for word in words[1:]]

    # Join the words together without spaces
    def_name = ''.join(case_words)

    return def_name

def downloadFontSource(name):
    font_name = get_default_font_name(name)
    local_font_path = "../fonts/" + font_name + '-Regular.ttf'
    return {"src": local_font_path, "name": name}

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
        
    return "../" + save_path

def get_contents(pageContent, pageName):
    # Example of parsing text and image positions from Fabric.js JSON
    elements = []
    rect_elements = []
    image_elements = []
    fonts = []
    font_names = ['arial']
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
            if(obj['fontFamily']):
                if(obj['fontFamily'] not in font_names):
                    font_names.append(obj['fontFamily'])
                    fonts.append(downloadFontSource(obj['fontFamily']))
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
    
    html_content = '<!DOCTYPE html><html><head><style>'
    for font in fonts:
        html_content += "@font-face{font-family:"
        html_content += font["name"] + ";\n"
        html_content += "src: url(" + font["src"] + ");\n" + "}\n"
        

    html_content += 'body { position: relative; }'
    html_content += '</style></head>'

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

    html_content += '</body></html>'

    # Save HTML content to a file
    with open(f'./html/{pageName}.html', 'w') as f:
        f.write(html_content)
        
for pageData in epub_data["book_pages"]:
    get_contents(pageData["page_content"], pageData["page_number"])
