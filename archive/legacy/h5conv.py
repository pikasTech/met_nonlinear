import numpy as np
import h5py
import shutil

HDF5_OBJECT_HEADER_LIMIT = 64512


def load_attributes_from_hdf5_group(group, name):
    """Loads attributes of the specified name from the HDF5 group."""
    if name in group.attrs:
        data = [
            n.decode('utf8') if hasattr(n, 'decode') else n
            for n in group.attrs[name]
        ]
    else:
        data = []
        chunk_id = 0
        while f'{name}{chunk_id}' in group.attrs:
            data.extend([
                n.decode('utf8') if hasattr(n, 'decode') else n
                for n in group.attrs[f'{name}{chunk_id}']
            ])
            chunk_id += 1
    return data


def filter_for_h5(input_filepath, output_filepath):
    """Filters and removes specific weights in the HDF5 file."""
    # 创建新文件的副本
    shutil.copy(input_filepath, output_filepath)

    # 打开副本文件进行操作
    with h5py.File(output_filepath, mode='r+') as f:
        layer_names = load_attributes_from_hdf5_group(f, 'layer_names')
        filtered_layer_names = []

        for name in layer_names:
            g = f[name]
            weight_names = load_attributes_from_hdf5_group(g, 'weight_names')
            if weight_names:
                filtered_layer_names.append(name)

        layer_names = filtered_layer_names

        # 遍历层并过滤权重
        for name in layer_names:
            g = f[name]
            weight_names = load_attributes_from_hdf5_group(g, 'weight_names')
            weight_values = [np.asarray(g[weight_name])
                             for weight_name in weight_names]

            # 检查是否需要移除权重
            for weight_name in list(weight_names):  # 使用 list() 避免动态修改时出错
                # if 'bias' in weight_name or 'spline_grid' in weight_name or 'scale_factor' in weight_name:
                if 'spline_grid' in weight_name or 'scale_factor' in weight_name:
                    print(f'Removing: {weight_name}')
                    del g[weight_name]  # 删除指定权重

            # 更新 weight_names 属性
            updated_weight_names = [w for w in weight_names if w in g]
            if 'weight_names' in g.attrs:
                del g.attrs['weight_names']
            g.attrs.create('weight_names', [n.encode(
                'utf8') for n in updated_weight_names])

    print(f"Filtered weights saved to {output_filepath}")


# 示例调用
input_file = 'projects\\FRIKANh8u6l6\\data\\old.fast_best.weights.h5'
output_file = 'projects\\FRIKANh8u6l6\\data\\fast_best.weights.h5'

filter_for_h5(input_file, output_file)
