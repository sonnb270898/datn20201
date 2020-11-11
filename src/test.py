import re
def read_ocr_file_without_box_entity_type(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        document_text = f.read()

    # match pattern in document: index,x1,y1,x2,y2,x3,y3,x4,y4,transcript
    regex = r"^\s*(-?\d+)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*," \
            r"\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,(.*)\n?$"

    matches = re.finditer(regex, document_text, re.MULTILINE)

    res = []
    for matchNum, match in enumerate(matches, start=1):
        index = int(match.group(1))
        points = [float(match.group(i)) for i in range(2, 10)]
        transcription = str(match.group(10))
        res.append((index, points, transcription))
    return res

# a=read_ocr_
import os
import glob

_product_pattern = r"([A-za-z]{3,})+"
result = re.search(_product_pattern, "Koobidehxx7", re.IGNORECASE)
print(result)