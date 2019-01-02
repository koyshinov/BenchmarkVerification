from scans.tools import get_controls_from_yaml


APPS = ("Access", "Excel", "InfoPath", "Outlook", "PowerPoint", "Publisher", "Word")


def main(scan_host):
    controls = get_controls_from_yaml("scripts\\cis_microsoft_office_2016\\controls.yml",
                                      "users_sid_each_app")
    transport = scan_host.get_transport("registry")

    sids = transport.get_sids_with_path("Software\\Microsoft\\Office\\16.0")

    for c_id, control in controls.items():
        if not sids:
            data = [{
                "type": "message",
                "data": {
                    "head": "Not Applicable",
                    "text": "Not found active users with installed Microsoft Office"
                }
            }]
            scan_host.add_control(c_id, status=3, result=data)
            continue

        good = True
        data = list()

        name = control["name"]
        compliant_values = control['compliant_values']

        for sid in sids:
            username = transport.username.get(sid, sid)

            for app in APPS:
                path = control["path"].format(sid=sid, app=app)
                value = transport.get_value(path, name)
                if value not in compliant_values:
                    good = False
                    status_print = "Not compliant"
                else:
                    status_print = "Compliant"

                data.append([username, app, name, value, ", ".join(map(str, compliant_values)),
                             status_print])

        result = [{
            "type": "table",
            "data": {
                "head": ["User", "App", "Name", "System", "Compliant values", "Status"],
                "body": data
            }
        }]
        if good:
            status = 1
        else:
            status = 2

        scan_host.add_control(c_id, status=status, result=result)
