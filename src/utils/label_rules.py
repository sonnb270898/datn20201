import re
import datetime 
from dateutil.parser import parse

# _price_pattern = r"\d+(\s*(\\,)?\.?\s*)\d+"
_price_pattern = r"\d+(\s*(\\,|\.|[a-zA-Z]+|;|:|'|\"|\s+){1,}\s*)\d+"
_product_pattern = r"([A-za-z]{2,})+"
_date_pattern = r"(\d+(\s*[/\-\.]\s*)\d+(\s*[/\-\.]\s*)\d+)"

total_synonym = ['total','grand','amt','balance','due']
tax_subtotal = ['subtotal','tax','item','qty','subtotai','sub-total','sub-totai']

min_distance_price_price_x = 50
min_distance_product_price_x = 150
min_distance_total_total_x = 50
min_distance_total_price_x = 100
W,H = (480,960)

def find_neighbor_label(boxes, index, label):
    i = index-1
    j = index+1
    dis_i = 99999
    dis_j = 99999
    boxes_len = len(boxes)
    while i>=0:
        if (boxes[i][3] == label):
            if label == 'product' and boxes[i][1][0] < W/2:
                break
            elif label == 'price' and boxes[i][1][0] > W/2:
                break
            elif label == 'total' and boxes[i][1][0] < 225:
                break
        i-=1
    while j<boxes_len:
        if (boxes[j][3] == label):
            if label == 'product' and boxes[j][1][0] < W/2:
                break
            elif label == 'price' and boxes[j][1][0] > W/2:
                break
            elif label == 'total' and boxes[j][1][0] < 225:
                break
        j+=1
    if i != -1:
        dis_i = abs(boxes[i][1][1] - boxes[index][1][1]) 
    if j != boxes_len:
        dis_j = abs(boxes[j][1][1] - boxes[index][1][1])
    
    if i == -1 and j == boxes_len:
        return -1
    if dis_i - dis_j > 0:
        return j
    return i

def first_box_in_line(boxes, index):
    i = index
    while index > 0:
        if  boxes[index][1][0] > boxes[index-1][1][0] and \
            abs(boxes[index-1][1][1] - boxes[i][1][1]) < abs(boxes[i][1][1] - boxes[i][1][-1]):
            index-=1
        else:
            return index
    return 1

def is_price(boxes, index):
    result = re.search(_price_pattern, boxes[index][2]+'0', re.IGNORECASE)
    if result:
        boxes[index][2] = boxes[index][2].replace(result.group(1),'.') + '0'

    if result and (boxes[index][1][0] > W/2):
        # if result.group(1) != '':
        #     boxes[index][2] = boxes[index][2].replace(result.group(1),'.')
        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')

        fb = first_box_in_line(boxes, index)
        is_in_total_region = any([True if i in boxes[fb][2].lower() else False for i in tax_subtotal])
        if boxes[index][3] == 'other':
            if  is_in_total_region:
                return False
            if  abs(boxes[fb][1][0] - boxes[product_nb][1][0]) > min_distance_price_price_x or\
                (boxes[fb-1][3] == 'price' and boxes[fb][3] == 'other'):
                return False

        #check distance product_product & product_price(theo x va y) 
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][2] -  boxes[price_nb][1][2]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[product_nb][1][1] -  boxes[product_nb][1][-1])+15):
                return True
        elif product_nb != -1 and price_nb == -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[product_nb][1][1] -  boxes[product_nb][1][-1])+15):
                return True
        elif product_nb == -1:
            return False
    return False

def is_product(boxes, index):
    result = re.search(_product_pattern, boxes[index][2], re.IGNORECASE)
    is_in_total_region = any([True if i in boxes[index][2].lower() else False for i in tax_subtotal])
    if result and (boxes[index][1][0] < W/2) and not is_in_total_region:
        if re.search(_price_pattern, boxes[index][2], re.IGNORECASE):
            return True
        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')
        #check distance product_product & product_price(theo x va y)
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[price_nb][1][1] -  boxes[price_nb][1][-1])+15):
                return True
        elif product_nb == -1 and price_nb != -1:
            if  (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[price_nb][1][1] -  boxes[price_nb][1][-1])+15):
                return True
        elif price_nb == -1:
            return False
        return False
    return False


def is_total(boxes, index):
    result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
    if result:
        boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

    if not result and boxes[index][3] == 'total':
        # boxes[index][3] = 'subtotal'
        return 'total', True

    if result and (boxes[index][1][1]) > H/4:
        total_nb = find_neighbor_label(boxes,index,'total')
        #check distance total_total & total_price(theo x va y) 
        if total_nb != -1:
            if re.search(_price_pattern, boxes[total_nb][2], re.IGNORECASE):
                return 'other',False
            elif (abs(boxes[index][1][0] -  boxes[total_nb][1][0]) >= min_distance_total_total_x) and \
                (abs(boxes[index][1][1] -  boxes[total_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])*0.75):
                return 'total', True
        elif total_nb == -1 and index > 1:
            if any([True if t_nym in boxes[index][2].lower() else False for t_nym in total_synonym]):
                return 'subtotal', True
            elif any([True if t_nym in boxes[index-1][2].lower() else False for t_nym in total_synonym]):
                if abs(boxes[index-1][1][0] - boxes[index][1][0]) >= min_distance_total_total_x \
                    or (boxes[index-1][3] == 'total'):
                    boxes[index-1][3] = 'subtotal'
                    return 'subtotal', True
            elif any([True if t_nym in boxes[index-2][2].lower() else False for t_nym in total_synonym]):
                if abs(boxes[index-2][1][0] - boxes[index][1][0]) >= min_distance_total_total_x \
                    or (boxes[index-1][3] == 'total') :
                    boxes[index-2][3] = 'subtotal'
                    return 'subtotal', True
    return 'other', False

def get_final_total(boxes):
    idx = ((boxes[:,3]=="subtotal") | (boxes[:,3]=="total")).nonzero()[0]
    total_max, id_max = (0,-1)
    for i in idx:
        result = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
        if result:
            tmp = result.group(1).replace(' ','')
            if float(tmp) > total_max:
                total_max, id_max = (float(tmp), i)
        boxes[i][3] = 'other'
    if id_max != -1:
        current_i = idx.tolist().index(id_max) - 1
        boxes[id_max][3] = 'total'
        while current_i > -1:
            pre_box = boxes[idx[current_i]][1]
            # get label_box total in same line
            if abs(pre_box[1] - boxes[id_max][1][1]) <= 20:
                boxes[idx[current_i]][3] = 'total'
            current_i -= 1
    return boxes 
    
def convert_result_to_json(boxes):
    result = {}
    result['pp'] = []
    product = []
    price = []
    boxes_len = len(boxes)
    for i in range(boxes_len):
        if boxes[i][3] in ['product','price','total']:
            if boxes[i][3] == 'product':
                product.append(boxes[i][2])
                if i+1 < boxes_len and boxes[i+1][3] == 'price':
                    if len(price) != 0:
                        result['pp'].append(('\n'.join(product[:-1]),price[0]))
                        del product[:-1]
                        del price[0]
                    else:
                        del product[:-1]  
            elif boxes[i][3] == 'price':
                __price = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
                price.append(__price.group())
            elif boxes[i][3] == 'total':
                total = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
                if total:
                    result['total'] = total.group(1)
        if result.get('date','') == '':
            result['date'] = search_date(boxes[i][2])
    if len(price) != 0:
        result['pp'].append(('\n'.join(product[:]),price[0]))
    if result['date'] == '':
        result['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    return result

def search_date(text):
    date = ''
    try:
        date = parse(text, fuzzy_with_tokens=True).strftime("%Y-%m-%d")
        return date
    except:
        res = re.search(_date_pattern, text, re.IGNORECASE)
        if res:
            date = res.group(1).replace(' ','')
            return parse(date).strftime("%Y-%m-%d")
        return date
    return date

if __name__ == '__main__':
    boxes= [
        [1,1,'11111111','product'],
        [1,1,'22222222','product'],
        [1,1,'%123.12','price'],
        [1,1,'22222222','product'],
        [1,1,'22222222','product'],
        [1,1,'33333333','product'],
        [1,1,'#1233.1','price'],
        [1,1,'33333333','product'],
        [1,1,'44444444','product'],
        [1,1,'$12.21','price'],
        [1,1,'44444444','product'],
        [1,1,'44444444','product'],
        [1,1,'55555555','product'],
        [1,1,'12.21','price'],
        [1,1,'55555555','product'],
        [1,1,'55555555','product'],
        [1,1,'55555555','product'],
        [1,1,'total','total'],
        [1,1,'12.21','total']
    ]
    # print(convert_result_to_json(boxes))
    date = "20/1/1992"
    print(search_date(date)) 





