from scans.tools import get_controls_from_yaml


def main(scan_host):
    controls = get_controls_from_yaml("scripts\\cis_microsoft_office_2016\\controls.yml",
                                      "users_sid_encryption_check")
    transport = scan_host.get_transport("registry")

    sids = transport.get_sids_with_path("Software\\Microsoft\\Office\\16.0")
    providers = transport.sub_branches("HKLM\SOFTWARE\Microsoft\Cryptography\Defaults\Provider")

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

        for sid in sids:
            username = transport.username.get(sid, sid)
            path = control["path"].format(sid=sid)
            value = transport.get_value(path, name)

            if not value:
                good = False
                status_print = "Not compliant"
                data.append([username, name, value, status_print, "Value is None"])
                continue

            try:
                provider, encr_type, key_len = value.split(",")
            except ValueError:
                good = False
                status_print = "Not compliant"
                data.append([username, name, value, status_print, "Value format is incorrect"])
                continue

            if provider not in providers:
                good = False
                status_print = "Not compliant"
                data.append([username, name, value, status_print, "Provider not found"])
                continue

            status_print = "Compliant"
            data.append([username, name, value, status_print, "All good"])

        result = [{
            "type": "table",
            "data": {
                "head": ["User", "Name", "System", "Status", "Reason"],
                "body": data
            }
        }]
        if good:
            status = 1
        else:
            status = 2

        scan_host.add_control(c_id, status=status, result=result)
