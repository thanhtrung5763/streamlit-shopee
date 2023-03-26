def get_data(keys, dic):
    if keys:
        temp = dic
        for key in keys:
            if temp and key in temp.keys():
                temp = temp[key]
            else:
                return None
        return temp
    return None


if __name__ == '__main__':
    data = {
        'shape': None
    }
    get_data(['shape', 'name'], data)
