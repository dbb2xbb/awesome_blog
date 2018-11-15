old = [
    {
        'id':'beijing',
        'name':123
    },
    # {
    #     'id':'suzhou',
    #     'name':456
    # }
]

new = [
    {
        'id':'beijing',
        'desc':'123',
        'name': 123
    },
    {
        'id':'shanghai',
        'name':456
    }
]

tmp_dict=[]

for index, item in enumerate(new):
    for k,v in item.items():
        if len(old) > index:
            if k in old[index]:
                if old[index][k] != v:
                    old[index][k] = v
                else:
                    pass
            else:
                print('index is %s' % index)
                tmp_dict.append({k:v})

        else:
            tmp_dict.append(item)

print(tmp_dict)
