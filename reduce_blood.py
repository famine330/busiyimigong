import numpy as np

"""
用于神锻出图，计算需要使用的盾次数以及挨打次数

分别代表：
上星光大盾、小盾
下星光大盾、小盾
"""

small_shield_all = 400735+7605966
small_shield_ri = 400735+272501
small_shield_xing = 22591+428793
small_shield_none = 22591+15363

hit = 613047411-478999285
all_blood = 501412
now_shield = 207909734

n = 80

# print(record)
# 计算将血压到10%以下所需要使用的盾次数与攻击次数

record = {}
all_record = []
for all_number in range(n):
    for ri_number in range(n):
        for xing_number in range(n):
            for none_number in range(n):
                blood=all_blood+now_shield+small_shield_all*all_number+small_shield_ri*ri_number+small_shield_xing*xing_number+small_shield_none*none_number
        if blood<hit:
            continue
        hit_num = blood//hit
        res_blood = blood-hit_num*hit

        use_num = all_number+ri_number+xing_number+none_number
        
        if 0 < blood%hit < int(all_blood*0.09):      # 不能是10%，因为铠甲会回血
            record[res_blood] = record.get(res_blood, [])
            record[res_blood].append([use_num, all_number, ri_number, xing_number, none_number, hit_num])
            all_record.append([res_blood, use_num, all_number, ri_number, xing_number, none_number, hit_num])
            # print("*"*10)
            # print(f"使用小盾{small_s_up}次，使用大盾{big_s_up}次\n下铠甲使用小盾{small_s_down}次，使用大盾{big_s_down}次\n挨打{hit_num}次，剩余血量{res_blood}")

for k, v in record.items():
    print("*"*30)
    print(f"剩余血量为{k}的方案有：")
    print("")
    v.sort()
    for ele in v:
        # 总体操作次数大于40，过滤
        if ele[0]>40:
            continue
        print(f"总操作次数为{ele[0]}")
        print(f"刻印全上使用小盾{ele[1]}次\n日光刻印使用小盾{ele[2]}次\n星光刻印使用小盾{ele[3]}次\n无刻印使用小盾{ele[4]}次\n挨打{ele[5]}次")
        print("-"*10)

print("&"*30)
print("&"*30)
print("&"*30)
all_record.sort(key=lambda x:x[1])
print("最少次数操作：")
for i in range(min(10, len(all_record))):
    print(f"总操作次数为{all_record[i][1]}")
    print(f"刻印全上使用小盾{all_record[i][2]}次\n日光刻印使用小盾{all_record[i][3]}次\n星光刻印使用小盾{all_record[i][4]}次\n无刻印使用小盾{all_record[i][5]}次\n挨打{all_record[i][6]}次，剩余血量{all_record[i][0]}")
    print("-"*10)


print("搜索完毕")
