import os
import re

def find_url_tags_in_templates(root_dir):
    url_pattern = re.compile(r'{%\s*url\s+[\'"]([^\'"]+)[\'"]')
    results = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.html'):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    try:
                        content = file.read()
                        matches = url_pattern.findall(content)
                        
                        # Filter out URLs that already have namespaces
                        non_namespaced = [url for url in matches if ':' not in url]
                        
                        if non_namespaced:
                            results.append((filepath, non_namespaced))
                    except UnicodeDecodeError:
                        print(f"Error reading {filepath}")
    
    return results

if __name__ == "__main__":
    templates_dir = "templates"
    results = find_url_tags_in_templates(templates_dir)
    
    if results:
        print("Found non-namespaced URL tags in the following files:")
        for filepath, urls in results:
            print(f"\n{filepath}:")
            for url in urls:
                print(f"  - {url}")
    else:
        print("No non-namespaced URL tags found.")
