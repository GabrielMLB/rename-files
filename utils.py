import os
import random
import json
import numpy as np


def random_color(num_color, seed):
    random.seed(seed)
    colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])for _ in range(num_color)]
    return colors


def open_file(path):
    with open(path) as file:
        input_file = json.load(file)
    return input_file


def save_json(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)


def rename(file_path, file_name, new_name, new_type, file_type):

    for i in file_type:
        old_file = os.path.join(file_path, file_name + '.' + i)
        if os.path.exists(old_file):
            new_file = os.path.join(file_path, new_name + '.' + new_type)
            os.rename(old_file, new_file)
            return


def save_dict_to_file(path, dic):
    f = open(path, 'w')
    f.write(str(dic))
    f.close()


def work_order_extraction(input_json, field):
    temp = []
    for OS in input_json['to_process']['current_orders']:
        temp.append(OS[field])
    return temp


def work_order_group_extraction(input_json):
    wo_id = []
    ticket = []
    lat = []
    long = []
    area = []
    flow_rate = []
    mix = []
    start = []
    end = []

    for OS in input_json['to_process']['current_orders']:
        wo_id.append(OS['id'])
        ticket.append(OS['ticket'])
        mix.append(OS['mixture'])
        lat.append(OS['fields'][0]['latitude'])
        long.append(OS['fields'][0]['longitude'])
        if len(OS['fields']) > 1:
            temp = 0
            for i in range(len(OS['fields'])):
                temp += OS['fields'][i]['area']
            area.append(temp)
        else:
            area.append(OS['fields'][0]['area'])
        flow_rate.append(OS['flow_rate'])
        start.append(OS['tolerance_interval']['start'])
        end.append(OS['tolerance_interval']['end'])

    return wo_id, ticket, mix, lat, long, area, flow_rate, start, end


def equipment_info_extraction(inputs):
    eq_id = []
    length = []
    eff_speed = []
    for Eq in inputs['to_process']['equipments']:
        eq_id.append(Eq['id'])
        length.append(Eq['length'])
        eff_speed.append(Eq['mean_effective_speed'])
    return eq_id, length, eff_speed


def data_ini(inputs):
    data = dict()
    data['type'] = "FeatureCollection"
    data['features'] = []

    data['features'].append({
        'type': 'Feature',
        'geometry': {'type': 'Point',
                     'coordinates': [inputs['to_process']['equipments'][0]['clear_location']['longitude'],
                                     inputs['to_process']['equipments'][0]['clear_location']['latitude']]},
        'properties': {'marker-symbol': 'farm'}})
    return data


def data_equipment_ini(inputs):
    data = dict()
    data['type'] = "FeatureCollection"
    data['features'] = []

    colors = random_color(len(inputs['to_process']['equipments']), 5)
    count = 0
    for eq in inputs['to_process']['equipments']:
        if eq['clear_location']['longitude'] == eq['last_location']['longitude'] and eq['clear_location']['latitude'] \
                == eq['last_location']['latitude']:
            data['features'].append({
                'type': 'Feature',
                'geometry': {'type': 'Point',
                             'coordinates': [eq['clear_location']['longitude'],
                                             eq['clear_location']['latitude']]},
                'properties': {'marker-symbol': 'warehouse',
                               'marker - size': 'large',
                               'marker-color': colors[count],
                               'Equipment': eq['id'],
                               'Displacement Speed': eq['mean_displacement_speed'],
                               'Effective Speed': eq['mean_effective_speed'],
                               'Length': eq['length'],
                               'Longitude': eq['clear_location']['longitude'],
                               'Latitude': eq['clear_location']['latitude']
                               }})
        else:
            data['features'].append({
                'type': 'Feature',
                'geometry': {'type': 'Point',
                             'coordinates': [eq['clear_location']['longitude'],
                                             eq['clear_location']['latitude']]},
                'properties': {'marker-symbol': 'farm',
                               'marker - size': 'large',
                               'Equipment': eq['id']
                               }})

            data['features'].append({
                'type': 'Feature',
                'geometry': {'type': 'Point',
                             'coordinates': [eq['last_location']['longitude'],
                                             eq['last_location']['latitude']]},
                'properties': {'marker-symbol': 'car',
                               'marker - size': 'large',
                               'Equipment': eq['id'],
                               'Displacement Speed': eq['mean_displacement_speed'],
                               'Effective Speed': eq['mean_effective_speed'],
                               'Length': eq['length'],
                               'Longitude': eq['clear_location']['longitude'],
                               'Latitude': eq['clear_location']['latitude']
                               }})
        count += 1

    return data


def affinity_matrix(path, wo_id):
    affinity = open_file(path)

    matrix = np.zeros([len(wo_id), len(wo_id)])

    for i in range(len(wo_id)):
        for j in range(len(wo_id)):
            if i != j:
                matrix[i][j] = affinity[str(wo_id[i])+'_'+str(wo_id[j])] * -1

    return matrix


def affinity_distance(path, wo_id):
    affinity = open_file(path)
    a = {}

    for i in range(len(wo_id)):
        temp_dist = []
        temp_id = []
        temp_id_sort = []
        for j in range(len(wo_id)):
            if i != j:
                temp_id.append(wo_id[j])
                temp_dist.append(affinity[str(wo_id[i]) + '_' + str(wo_id[j])])

        for k in np.argsort(temp_dist):
            temp_id_sort.append(temp_id[k])
        a[str(wo_id[i])] = temp_id_sort

    return a


def input_equipment_list_extraction(inputs):
    eq_id = []
    for p in inputs:
        eq_id.append(p['id'])
    return sorted(np.unique(eq_id))


def equipment_list_extraction(inputs):
    eq_id = []
    for p in inputs:
        eq_id.append(p['id_equipment'])

    return sorted(np.unique(eq_id))


def write_excel_equipment_id(ws, eq_id_list, name, columns, origim, round_number):
    count = 0
    for i in eq_id_list:
        ws[columns[0] + str(origim + count)] = i
        ws[columns[0] + str(origim + 11 + count)] = i
        ws[columns[0] + str(origim + 22 + count)] = i
        ws[columns[0] + str(origim + 33 + count)] = i
        ws[columns[0] + str(origim + 44 + count)] = i
        ws[columns[0] + str(origim + 55 + count)] = i
        count += 1

    for j in range(round_number):
        ws[columns[j * 2 + 1] + str(origim - 1)] = name[0]
        ws[columns[j * 2 + 2] + str(origim - 1)] = name[1]


def write_excel_template(inputs, ws, eq_id_list, columns, ex, origim):
    for p in inputs:
        row = eq_id_list.index(p['id_equipment'])
        column = p['round']
        # worked_area
        ws[columns[column * 2 + ex] + str(origim + row)] = p['worked_area']
        # worked_time
        ws[columns[column * 2 + ex] + str(origim + 11 + row)] = p['worked_time']
        # displacement_time
        ws[columns[column * 2 + ex] + str(origim + 22 + row)] = p['displacement_time']
        # wash_time
        ws[columns[column * 2 + ex] + str(origim + 33 + row)] = p['watch_time']


def write_excel_template_round0_details(output, ws, wo_id, mix, eq_id_list, columns, ex, origin):
    for dist in output:
        row = eq_id_list.index(dist['idEquipament'])
        wo_number = 0
        change_number = 0
        actual_mix = None
        for element in dist['trip']:
            if element != -1 and element != -2:
                if wo_number == 0:
                    actual_mix = mix[wo_id.index(element)]
                else:
                    if mix[wo_id.index(element)] == actual_mix:
                        pass
                    else:
                        change_number += 1
                        actual_mix = mix[wo_id.index(element)]
                wo_number += 1
        # Number of W.O.
        ws[columns[ex] + str(origin + 44 + row)] = wo_number
        # Change of products
        ws[columns[ex] + str(origin + 55 + row)] = change_number


def write_excel_aux(inputs, ws, columns, origin):
    for i, p in enumerate(inputs):
        # worked_area
        ws[columns[0] + str(origin + i)] = p['worked_area']
        # worked_time
        ws[columns[1] + str(origin + i)] = p['worked_time']
        # displacement_time
        ws[columns[2] + str(origin + i)] = p['displacement_time']
        # wash_time
        ws[columns[3] + str(origin + i)] = p['watch_time']
