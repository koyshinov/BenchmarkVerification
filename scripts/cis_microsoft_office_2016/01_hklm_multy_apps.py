import time

from scans.tools import get_controls_from_yaml


APPS = ("groove.exe", "excel.exe", "mspub.exe", "powerpnt.exe", "pptview.exe", "visio.exe",
        "winproj.exe", "outlook.exe", "spDesign.exe", "exprwd.exe", "msaccess.exe",
        "onenote.exe",  # FIXME: I'm onent.exe in gpedit
        "mse7.exe")

reg_base = r"HKLM\software\microsoft\internet explorer\main\featurecontrol"
reg_base_copy = r"HKLM\software\policies\microsoft\internet explorer\main\featurecontrol"


def prepare(controls, transport):
    for c_id, control in controls.items():
        path = control["path"]
        if reg_base not in path:
            raise NameError(f'Script corrupted. Control [{c_id}]')
        path_copy = path.replace(reg_base, reg_base_copy)
        transport.copy_branch(path, path_copy)
    time.sleep(0.1)


def delete_branches(controls, transport):
    for c_id, control in controls.items():
        path = control["path"]
        path_copy = path.replace(reg_base, reg_base_copy)
        transport.dele_branch(path_copy)


def main(scan_host):
    controls = get_controls_from_yaml("scripts\\cis_microsoft_office_2016\\controls.yml",
                                      "secur_app_sett")
    transport = scan_host.get_transport("registry")

    prepare(controls, transport)

    for c_id, control in controls.items():
        try:
            data = list()

            path = control["path"]
            path_copy = path.replace(reg_base, reg_base_copy)

            compliant_values = control['compliant_values']

            good = True

            for app in APPS:
                value = transport.get_value(path_copy, app)
                if value not in compliant_values:
                    # print(path, app, value)
                    status_print = "Not compliant"
                    good = False
                else:
                    status_print = "Compliant"

                data.append([app, value, ", ".join(map(str, compliant_values)), status_print])

            result = [{
                "type": "table",
                "data": {
                    "head": ["App", "System", "Compliant values", "Status"],
                    "body": data
                }
            }]

            if good:
                status = 1
            else:
                status = 2

            scan_host.add_control(c_id, status=status, result=result)

        except Exception as e:
            data = [{
                "type": "message",
                "data": {
                    "head": "Unknown script error",
                    "text": str(e)
                }
            }]
            scan_host.add_control(c_id, status=4, result=data)

    delete_branches(controls, transport)
