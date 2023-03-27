import glob
import json
import os
import time

import helper
import numpy as np
import pandas as pd
import requests
from constants import API_KEY
from pandas import json_normalize

BASE_IMG_URL = 'https://cf.shopee.com.my/file/'
OMINOUS_TAGGING_API = 'https://api.omnious.com/tagger/v2/tags'
headers = {
    'Host': 'api.omnious.com',
    'Content-Type': 'application/json',
    'x-api-key': API_KEY
}


def get_tag_data(image_url: str):
    '''
        Get tag's data response from Ominous API by sending image_url
    '''
    try:
        payload = json.dumps({
            "image": {
                "type": "url",
                "content": image_url
            },
            "context": {
                "detection": ["TOP", "BOTTOM", "WHOLEBODY", "SWIMWEAR", "SHOES"]
            }
        })
        response = requests.post(
            OMINOUS_TAGGING_API, headers=headers, data=payload)
        if response.status_code == 201:
            data = response.json()['data']
            return data
        return None
    except Exception as e:
        print(e)
        return None


def read_data(extract_path, type='json'):
    '''
        Read data from files
    '''
    li = []

    if type == 'json':
        files = glob.glob(os.path.join(
            extract_path, '**/*.json'), recursive=True)
        print(len(files))
        for file in files:
            f = open(file)
            df = json_normalize(json.load(f))
            li.append(df)
        files.clear()

        df = pd.concat(li, axis=0, ignore_index=True)
    elif type == 'csv':
        files = glob.glob(os.path.join(extract_path, '*.csv'))
        li = []
        print(len(files))
        for file in files:
            f = open(file)
            df = pd.read_csv(
                f, dtype={'shop_id': str, 'sb_shop_id': str, 'ctime': str, })
            li.append(df)
        files.clear()

        df = pd.concat(li, axis=0, ignore_index=True)

    return df


def example():
    # TESTING
    # get tag data from api
    img_url = 'https://image.wconcept.co.kr//productimg/image/img0/16/301034416_GG14947.jpg'
    tagger_data = get_tag_data(image_url=img_url)
    print(tagger_data)

def transform(data):
    '''
        Drop, rename cols
        Update price field
        Extract data from tier_variations field then store into 2 new columns called size, color
    '''
    
    columns = [
        'itemid',
        'shopid',
        'Scraping_day',
        'Stylebox_shop_ID',
        'product_link',
        'item_basic.name',
        'item_basic.images',
        'item_basic.currency',
        'item_basic.stock',
        'item_basic.ctime',
        'item_basic.sold',
        'item_basic.historical_sold',
        'item_basic.liked_count',
        'item_basic.cmt_count',
        'item_basic.item_status',
        'item_basic.price_min',
        'item_basic.price_max',
        'item_basic.price_min_before_discount',
        'item_basic.price_max_before_discount',
        'item_basic.raw_discount',
        'item_basic.tier_variations',
        'item_basic.item_rating.rating_star',
        'item_basic.item_rating.rating_count',
        'item_basic.item_rating.rcount_with_context',
        'item_basic.item_rating.rcount_with_image',
        'item_basic.shopee_verified',
        'item_basic.is_official_shop',
        'item_basic.video_info_list',
    ]
    data = data[columns]
    data.rename(columns={
        'itemid': 'item_id',
        'shopid': 'shop_id',
        'Scraping_day': 'scraping_day',
        'Stylebox_shop_ID': 'sb_shop_id',
        'product_link': 'url',
        'item_basic.name': 'name',
        'item_basic.images': 'images',
        'item_basic.currency': 'currency',
        'item_basic.stock': 'stock',
        'item_basic.ctime': 'ctime',
        'item_basic.sold': 'sold',
        'item_basic.historical_sold': 'historical_sold',
        'item_basic.liked_count': 'liked_count',
        'item_basic.cmt_count': 'cmt_count',
        'item_basic.item_status': 'item_status',
        'item_basic.price_min': 'price_min',
        'item_basic.price_max': 'price_max',
        'item_basic.price_min_before_discount': 'price_min_before_discount',
        'item_basic.price_max_before_discount': 'price_max_before_discount',
        'item_basic.raw_discount': 'raw_discount',
        'item_basic.tier_variations': 'tier_variations',
        'item_basic.item_rating.rating_star': 'rating_star',
        'item_basic.item_rating.rating_count': 'rating_count',
        'item_basic.item_rating.rcount_with_context': 'rcount_with_context',
        'item_basic.item_rating.rcount_with_image': 'rcount_with_image',
        'item_basic.shopee_verified': 'shopee_verified',
        'item_basic.is_official_shop': 'is_official_shop',
        'item_basic.video_info_list': 'video_info_list',
    }, inplace=True)

    data['item_id'] = data['item_id'].apply(lambda x: f"s_{x}")

    min_discount_price = data['price_min'] // 100000
    max_discount_price = data['price_max'] // 100000
    data['price_min'] = min_discount_price
    data['price_max'] = max_discount_price

    # OPTIMIZED from 6sec to 0.2sec
    price_max_before_discount_lst = [(pmbd // 100000) if pmbd != -1 else pm for pmbd, pm in zip(data['price_max_before_discount'], data['price_max'])]
    price_min_before_discount_lst = [(pmbd // 100000) if pmbd != -1 else pm for pmbd, pm in zip(data['price_min_before_discount'], data['price_min'])]
    data['price_max_before_discount'] = price_max_before_discount_lst
    data['price_min_before_discount'] = price_min_before_discount_lst

    colors = []
    sizes = []
    # OPTIMIZED from 6sec to 1sec
    for i, row in zip(data.index, data['tier_variations']):
        a = False
        b = False
        images = None
        if type(row) == list:
            for var in row:
                name = var['name']
                if name:
                    if not a and name[0] in ['M', 'C']:
                        colors.append(','.join(var['options']))
                        a = True
                        images = var.get('images')
                    elif not b and name[0] in ['S', 'K']:
                        sizes.append(','.join(var['options']))
                        b = True
            
            if a and images:
                data.at[i, 'images'] = images

        if not a:
            colors.append(np.nan)

        if not b:
            sizes.append(np.nan)    

    print(len(colors))
    print(len(sizes))
    data['color'] = colors
    data['size'] = sizes

    data['name'] = data['name'].apply(
        lambda x: x[(x.rfind(']') + 1):].strip() if '[' in x and ']' in x else x)
    data.drop(columns=['tier_variations'], inplace=True)

    return data

def transform_tag_data(tag_datas):
    '''
        Transform tag_data from response into dataframe
    '''
    
    tags_cols = []
    for tag_data in tag_datas:
        objects = helper.get_data(['taggingResult','objects'], tag_data)
        tag_cols = {}
        tag_cols['item_id'] = helper.get_data(['id'], tag_data)
        if objects:
            product_type = helper.get_data(['type'], objects[0])
            if product_type == 'CLOTHING':
                tags = helper.get_data(['tags'], objects[0])
                if tags:
                    tag_cols['category'] = helper.get_data(['category', 'name'], tags[0])
                    tag_cols['sub_category'] = helper.get_data(['item', 'name'], tags[0])
                    colors = helper.get_data(['colors'], tags[0])
                    if colors:
                        tag_cols['tag_color'] = helper.get_data(['name'], colors[0])
                    else:
                        tag_cols['tag_color'] = None
                    tag_cols['length'] = helper.get_data(['length', 'name'], tags[0])
                    tag_cols['sleeve_length'] = helper.get_data(['sleeveLength', 'name'], tags[0])
                    tag_cols['neck_line'] = helper.get_data(['neckLine', 'name'], tags[0])
                    tag_cols['fit'] = helper.get_data(['fit', 'name'], tags[0])
                    tag_cols['shape'] = helper.get_data(['shape', 'name'], tags[0])
                    prints = helper.get_data(['prints'], tags[0])
                    textures = helper.get_data(['textures'], tags[0])
                    details = helper.get_data(['details'], tags[0])
                    looks = helper.get_data(['looks'], tags[0])
                    if prints:
                        tag_cols['print'] = helper.get_data(['name'], prints[0])
                    else:
                        tag_cols['print'] = None
                    
                    if textures:
                        tag_cols['texture'] = helper.get_data(['name'], textures[0])
                    else:
                        tag_cols['texture'] = None 

                    if details:
                        tag_cols['detail'] = helper.get_data(['name'], details[0])
                    else:
                        tag_cols['detail'] = None
                    
                    if looks:
                        tag_cols['look'] = helper.get_data(['name'], looks[0])
                    else:
                        tag_cols['look'] = None
        else:
            tag_cols['category'] = None
            tag_cols['sub_category'] = None
            tag_cols['tag_color'] = None
            tag_cols['length'] = None
            tag_cols['sleeve_length'] = None
            tag_cols['neck_line'] = None
            tag_cols['fit'] = None
            tag_cols['shape'] = None
            
            tag_cols['print'] = None
            tag_cols['texture'] = None 
            tag_cols['detail'] = None
            tag_cols['look'] = None              
        
        tags_cols.append(tag_cols)

    tag_tdf = pd.DataFrame(tags_cols)
    return tag_tdf

def merge_tag_tdf(product_data, tag_data):
    '''
        Merge product_data with tag_data
    '''

    merged_tdf = product_data.merge(tag_data, on='item_id')
    return merged_tdf

def req_step1(payload, method, task_id):
    '''
        If the method is POST, means doesnt have task then create task with all images in payload
        If the method is PUT, means already have task then update task with all images in payload
    '''

    # Bulk Step 1
    OMINOUS_BULK_TAGGING_API = 'https://api.omnious.com/tagger/v2.12/bulk'
    if method == 'POST':
        r = requests.request(method=method, url=OMINOUS_BULK_TAGGING_API, headers=headers, data=json.dumps(payload))
        data = r.json()
        # get taskId
        task_id = data['taskId']
    elif method == 'PUT':
        OMINOUS_BULK_TAGGING_API = f'{OMINOUS_BULK_TAGGING_API}/{task_id}'
        r = requests.request(method=method, url=OMINOUS_BULK_TAGGING_API, headers=headers, data=json.dumps(payload))
    return task_id

def req_step2(task_id):
    '''
        Check status of task. If the task is DONE, return number of images that done(have tag_data)
    '''

    # Bulk Step 2
    while True:
        time.sleep(10)
        OMINOUS_BULK_TAGGING_STATUS_API = f'https://api.omnious.com/tagger/v2.12/bulk/{task_id}/status/'
        r = requests.get(OMINOUS_BULK_TAGGING_STATUS_API, headers=headers)
        response = r.json()
        data = response['data']
        # get taskStatus and stats of how many done, fail, processing
        task_status = data['taskStatus']
        task_stats = data['count']
        if task_status == 'TASK_DONE':
            print('end of task') 
            return data['count']['done']
        else:
            print(task_stats)
            time.sleep(13) # :)
    
def req_step3(task_id):
    '''
        Fetch tag_data using task_id
    '''

    # Bulk Step 3
    OMINOUS_BULK_TAGGING_RESULT_API = f'https://api.omnious.com/tagger/v2.12/bulk/{task_id}'
    offset = 0
    tag_datas = []
    while True:
        params = {
            'offset': offset,
            'size': 100
        }
        r = requests.get(OMINOUS_BULK_TAGGING_RESULT_API, headers=headers, params=params)
        response = r.json()
        data_response = response['data']
        size_results = len(data_response['results'])
        print('size of results: ', size_results)
        
        tag_datas.extend(data_response['results'])
        offset += 100
        if offset > data_response['taskInfo']['totalCount']:
            print(f"fetch: {data_response['taskInfo']['totalCount']} of {data_response['taskInfo']['totalCount']}")
            break
        else:
            print(f"fetch: {offset} of {data_response['taskInfo']['totalCount']}")
    
    return tag_datas

def bulk_tag_product_put(product_tdf):
    '''
        For the first request POST, we upload 500 images(the api will create the task)
        After that, we put 1000 images each request PUT(the api will update the task above)
        After the task is DONE, return task_id
    '''

    begin = 0
    end = 500
    size_df = len(product_tdf)
    if end > size_df:
        end = size_df
    task_id = None
    while True:
        print(f'begin: {begin}, end: {end}')
        tag_reqs = []
        # ttest_tdf = test_tdf.iloc[begin:end]
        for i, row in product_tdf[begin:end].iterrows():
            # print(i)
            id = row['item_id']
            image = row['images'][0]
            tag_req = {
                'image': {
                    'type': 'url',
                    'content': f'{BASE_IMG_URL}{image}'
                },
                'context': {
                    'id': id
                }
            }
            tag_reqs.append(tag_req)
            # for image in images:
            #     tagger_data = get_tag_data(f'{BASE_IMG_URL}{image}')
            #     print(tagger_data)

        payload_bulk_manual = {
            "option": ["STRICT"],
            "defaultDetection": ["TOP", "BOTTOM", "WHOLEBODY", "SWIMWEAR"],
            "description": "Description",
            "taggingRequest": tag_reqs
        }   
        if begin == 0:
            task_id = req_step1(payload=payload_bulk_manual, method='POST', task_id=None)
        else:
            task_id = req_step1(payload=payload_bulk_manual, method='PUT', task_id=task_id)
        if end == size_df:
            break
        begin = end
        end += 1000
        if end > size_df:
            end = size_df
    req_step2(task_id=task_id)
    # tag_datas = req_step3(task_id=task_id, no_done=no_done)
    return task_id

def match_tag_data(product_tdf, tag_tdf):
    '''
        Filter to only get products havent been tagged
        If this df not empty, then send all images using api, UPDATE tag_tdf

        Then merge product_tdf and tag_tdf together
    '''
    product_tdf_not_tag = product_tdf.drop_duplicates(subset=['item_id']).loc[~product_tdf['item_id'].isin(tag_tdf['item_id'])][['item_id', 'images']]
    print(len(product_tdf_not_tag))
    if not product_tdf_not_tag.empty:
        task_id = bulk_tag_product_put(product_tdf_not_tag)

        tag_datas = fetch_tag_data(str(task_id))
        tag_tdf_new = transform_tag_data(tag_datas=tag_datas)

        # tag_tdf_new_no_empty = tag_tdf.loc[~tag_tdf_new['category'].isnull()]

        tag_tdf = tag_tdf.append(tag_tdf_new).reset_index(drop=True)
        
    data_tagged = merge_tag_tdf(product_tdf, tag_tdf)
    return data_tagged  

def fetch_tag_data(task_id='20bad2a9-4201-46c1-a4ff-c1fab0140438'):
    '''
        Fetch tag data from task(this task include multiple response)
    '''

    no_done = req_step2(task_id=task_id)
    while True:
        tag_datas = req_step3(task_id=task_id)
        if len(tag_datas) == no_done:
            break
        else:
            time.sleep(3.5)  
    return tag_datas

def load_data(data_tagged_clothing):
    '''
        Load data that have been tagged to file
    '''

    load_path = '/Users/thanhninh/Documents/abc-studio/day3-streamlit/shopee-streamlit/data_with_tag'
    for scraping_day in data_tagged_clothing['scraping_day'].unique().tolist():
        data_day = data_tagged_clothing[data_tagged_clothing['scraping_day'] == scraping_day]

        data_day.to_csv(f'{load_path}/data_tagged_{scraping_day}.csv', index=False)

def main():
    extract_path = '/Users/thanhninh/Documents/abc-studio/day3-streamlit/shopee-streamlit/data'
    data = read_data(extract_path)
    data = transform(data)

    # CASE 1: Already has tag data, then fetch by task_id
    tag_datas = fetch_tag_data()
    tag_tdf = transform_tag_data(tag_datas=tag_datas)
    
    # CASE 2: Do not have any task data before, so we get data of one day first, bulk it. After that, fetch by task_id
    # task_id, no_done = bulk_tag_product_put(product_tdf=data)
    # tag_datas = bulk_fetch_tag_data(task_id=task_id)
    # tag_tdf = transform_tag_data(tag_datas=tag_datas)

    data_tagged = match_tag_data(product_tdf=data, 
    tag_tdf=tag_tdf)

    data_tagged_clothing = (data_tagged[~data_tagged['category'].isnull()])
    load_data(data_tagged_clothing)

if __name__ == '__main__':
    main()
