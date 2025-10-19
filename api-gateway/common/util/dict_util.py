# edit at 2024-03-31
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

from datetime import datetime, date, timedelta
from argparse import Namespace
import decimal

from common.util.RoPrinter import RoPrinter
printer = RoPrinter('dict_util')
rp = printer.rp

def is_diff(me, new_entry):

    me = Namespace(**me)
    new_entry = Namespace(**new_entry)

    # compare all fields
    result = []
    for k, v in vars(new_entry).items():
        if k == 'gijun_date' or k == 'gijun_date_str' or k == 'created_date' or k == 'created_at' or k == 'updated_at' or k == 'ro_gijun_date' or k == 'ro_gijun_date_str' or k == 'is_processed' or k == '원천도형ID' or k == 'center': # 센터는 geom 다를 때 판단
            continue
        if k == 'id' or k == 'bbox':
            continue
        if k == 'geom':
            me_geom = getattr(me, k)
            new_geom = v
            me_geom_str = str(me_geom)
            new_geom_str = str(new_geom)
            if me_geom_str != new_geom_str:
                # rp(f'[{me.id}] geom is different')
                # 약간 위치를 이동하는 경우가 있음
                # 센터와 면적을 비교하여 크게 차이가 안 나면 같은 것으로 봄

                ## 센터 비교
                me_center = me_geom.centroid
                new_center = new_geom.centroid
                if f'{me_center.x:.6f}' == f'{new_center.x:.6f}' and f'{me_center.y:.6f}' == f'{new_center.y:.6f}':
                    me_area = me_geom.area
                    new_area = new_geom.area
                    ## 면적 비교
                    if f'{me_area:.6f}' == f'{new_area:.6f}':
                        ## 센터가 거의 같고, 면적이 거의 같으면 그냥 넘어감
                        continue
                    else:
                        to_append = f'{k}: geom diff, center: {me_center}->{new_center}, area: {me_area}->{new_area}'
                        rp(to_append)
                        result.append(to_append)

        # date일 경우 str으로 바꿔서 비교
        me_v = getattr(me, k)
        if isinstance(me_v, date):
            me_v = me_v.strftime('%Y-%m-%d')
        if isinstance(v, date):
            v = v.strftime('%Y-%m-%d')

        # float일 경우 round하여 비교
        if isinstance(me_v, float):
            if k == 'x' or k == 'y':
                me_v = round(me_v, 6)
            else:
                me_v = round(me_v, 2)
        if isinstance(v, float):
            if k == 'x' or k == 'y':
                v = round(v, 6)
            else:
                v = round(v, 2)

        # decimal일 경우 float->round하여 비교
        # x,y를 제외하고는 소숫점 두자리까지 비교
        if isinstance(me_v, decimal.Decimal):
            if k == 'x' or k == 'y':
                me_v = round(float(me_v), 6)
            else:
                me_v = round(float(me_v), 2)
                # print('----------------------', k, me_v)

        if isinstance(v, decimal.Decimal):
            if k == 'x' or k == 'y':
                v = round(float(v), 6)
            else:
                v = round(float(v), 2)
                # print('----------------------', k, v)

        # print('me_v', k, me_v, type(me_v))
        # print('v', k, v, type(v))

        if me_v != v and k != 'geom':
            code = getattr(me, 'code')
            rep = code or me.id
            rp(f'[{rep}] {k} is different {me_v} != {v}')
            result.append(f'{k}:{me_v}->{v}')

    if len(result) > 0:
        return True, result
    return False, None

def merge_json(json1, json2):
    import json
    print('json1', json1)
    print('json2', json2)
    dict1 = json.loads(json1) if json1 else {}
    dict2 = json.loads(json2) if json2 else {}
    return json.dumps({**dict1, **dict2}, ensure_ascii=False)