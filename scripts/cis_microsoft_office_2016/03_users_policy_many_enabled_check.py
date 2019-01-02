from scans.tools import get_controls_from_yaml


REG_VALUES_MAP = {
    "msoridcuxdocspropertypanelbeaconing": {
        0: "Never show UI",
        1: "Always show UI",
        2: "Show UI if XSN is in Internet Zone",
    },
    "disableblog": {
        0: "Enabled",
        1: "Only SharePoint blogs allowed",
        2: "All blogging disabled",
    },
    "signinoptions": {
        0: "Both IDs allowed",
        1: "Microsoft Account only",
        2: "Org ID only",
        3: "None allowed",
    },
    "automationsecurity": {
        1: "Macros enabled",
        2: "Use application macro security level",
        3: "Disable macros by default",
    },
    "useonlinecontent": {
        0: "Do not allow Office to connect to the Internet",
        2: "Allow Office to connect to the Internet",
    }
}


def main(scan_host):
    controls = get_controls_from_yaml("scripts\\cis_microsoft_office_2016\\controls.yml",
                                      "users_sid_many_enabled_check")
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
            path = control["path"].format(sid=sid)
            value = transport.get_value(path, name)

            if value not in compliant_values:
                good = False
                status_print = "Not compliant"
            else:
                status_print = "Compliant"

            value_print = "{} ({})".format(
                value, REG_VALUES_MAP.get(name, {}).get(value, "Not configured / Disabled"))

            data.append([username, name, value_print, ", ".join(map(str, compliant_values)),
                         status_print])

        result = [{
            "type": "table",
            "data": {
                "head": ["User", "Name", "System", "Compliant values", "Status"],
                "body": data
            }
        }]
        if good:
            status = 1
        else:
            status = 2

        scan_host.add_control(c_id, status=status, result=result)
