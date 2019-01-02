from scans.tools import get_controls_from_yaml


def main(scan_host):
    controls = get_controls_from_yaml("scripts\\cis_microsoft_office_2016\\controls.yml",
                                      "updates_check")
    transport = scan_host.get_transport("registry")

    for c_id, control in controls.items():
        path = control["path"]
        name = control["name"]
        compliant_values = control['compliant_values']

        value = transport.get_value(path, name)

        if value in compliant_values:
            status = 1
            status_print = "Compliant"
        else:
            status = 2
            status_print = "Not compliant"

        data = [{
            "type": "table",
            "data": {
                "head": ["Name", "System", "Compliant values", "Status"],
                "body": [
                    [name, value, ", ".join(map(str, compliant_values)), status_print]
                ]
            }
        }]
        scan_host.add_control(c_id, status=status, result=data)
