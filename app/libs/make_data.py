# _*_ coding:utf-8 _*_
import json

__author__ = 'meto'
__date__ = '2019/8/13 15:15'


def caijian_save_data(form, frame):
    """
    裁剪保存的数据处理
    :param form:
    :param frame:
    :return:
    """
    data = {'photo_path': form.get('photo_path'), 'task_id': form.get('task_id'),
            'task_detail_id': form.get('task_detail_id'), 'split_type': frame.get('split_type'),
            'coordinate': frame.get('coordinate'), 'final_coordinate': frame.get('final_coordinate'),
            'graph_index': frame.get('graph_index'), 'pic_type': frame.get('pic_type'),
            'operate_user': form.get('create_user')}

    return data


def label_save_data(form, prop):
    if prop.get('prop_type') == 5:
        prop_option_value = json.dumps(prop.get('prop_option_value'))
        prop_option_value_final = json.dumps(prop.get('prop_option_value'))
    else:
        prop_option_value = str(prop.get('prop_option_value'))
        prop_option_value_final = str(prop.get('prop_option_value'))
    data = {'photo_path': form.get('photo_path'), 'task_id': form.get('task_id'),
            'task_detail_id': form.get('task_detail_id'), 'create_user': form.get('create_user'),
            'prop_id': prop.get('prop_id'), 'prop_option_value': prop_option_value,
            'prop_option_value_final': prop_option_value_final, 'prop_type': prop.get('prop_type')}
    return data


def caijian_modify_data(form, frame):
    data = {'photo_path': form.get('photo_path'), 'task_id': form.get('task_id'),
            'task_detail_id': form.get('task_detail_id'), 'split_type': frame.get('split_type'),
            'coordinate': frame.get('coordinate'), 'final_coordinate': frame.get('final_coordinate'),
            'graph_index': frame.get('graph_index'), 'pic_type': frame.get('pic_type'),
            'operate_user': form.get('create_user')}
    return data


def label_modify_data(form, prop):
    if prop.get('prop_type') == 5:
        prop_option_value = json.dumps(prop.get('prop_option_value'))
        prop_option_value_final = json.dumps(prop.get('prop_option_value'))
    else:
        prop_option_value = str(prop.get('prop_option_value'))
        prop_option_value_final = str(prop.get('prop_option_value'))
    data = {'photo_path': form.get('photo_path'), 'task_id': form.get('task_id'),
            'task_detail_id': form.get('task_detail_id'), 'create_user': form.get('create_user'),
            'prop_id': prop.get('prop_id'), 'prop_option_value': prop_option_value,
            'prop_option_value_final': prop_option_value_final, 'prop_type': prop.get('prop_type')}
    return data


def check_modify_data(form, frame):
    data = {'photo_path': form.get('photo_path'), 'task_id': form.get('task_id'),
            'task_detail_id': form.get('task_detail_id'), 'split_type': frame.get('split_type'),
            'coordinate': frame.get('coordinate'), 'final_coordinate': frame.get('final_coordinate'),
            'graph_index': frame.get('graph_index'), 'pic_type': frame.get('pic_type'),
            'operate_user': form.get('create_user')}
    return data
