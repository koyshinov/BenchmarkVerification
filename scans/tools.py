import yaml


def get_data_from_yaml(filename):
    with open(filename) as file:
        yaml_data = file.read()
        recoms = yaml.load(yaml_data)

    return recoms


def get_controls_from_yaml(filename, r_type=None):
    controls = get_data_from_yaml(filename)

    if r_type:
        controls = {r_id: r_data for r_id, r_data in controls.items() if r_data["type"] == r_type}

    return controls
