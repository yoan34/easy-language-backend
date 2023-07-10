import json


with open("orders_239.json", "r") as f:
    data = json.load(f)

total_lig = 0
total_lig_to_update = {}

# for order in data['orders']:
#     print(order['id'])
lig_good_state = {}
for order in data['orders']:
    total_lig += len(order['order_items'])
    for lig in order['line_item_groups']:
        if lig['state'] in ['claimed_orderable', 'claimed_warehouse_orderable']:
            lig_good_state[lig['order_item_id']] = lig

    for order_item in order['order_items']:
        if order_item['id'] not in lig_good_state:
            continue
        if 'supplier_response' in order_item['information']:
            if 'status' in order_item['information']['supplier_response']:
                if order_item['information']['supplier_response']['status'] not in [201, 206]:
                    total_lig_to_update[order_item['id']] = order_item
            else:
                total_lig_to_update[order_item['id']] = order_item
        else:
            total_lig_to_update[order_item['id']] = order_item

title = f"{len(data['orders'])} concerné du 20/06/2023 00h au 30/06/2023 00h"
print(f"{title:-^80}\n")
print(f"Total order items                 : {total_lig}")
print(f"Total LIG dans le bon état        : {len(lig_good_state)} ('claimed_orderable' ou 'claimed_warehouse_orderable')")
print(f"Total LIG à re-envoyer API Cultura: {len(total_lig_to_update)} (qui n'as pas de information.supplier_response ou qui n'est pas au status 201)")
print(f"\n{'tous les orders ID avec leur LIG à re-envoyer à API Cultura':-^80}")
for order in data['orders']:
    order_items = []
    for order_item in order['order_items']:
        if order_item['id'] in total_lig_to_update:
            order_items.append(order_item['id'])
    print(f"{order['id']}={order_items}") if order_items else None


