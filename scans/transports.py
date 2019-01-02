import winreg
import re
import wmi
import pythoncom


class RegistryTransport:
    # TODO: Optimize all queries
    def __init__(self, host, user, passw):
        pythoncom.CoInitialize()
        self.wmi_client = wmi.WMI(computer=host, user=user, password=passw)
        self.reg_conn = self.wmi_client.StdRegProv
        # TODO: Append all types (maybe)
        self.give_value_method = {
            winreg.REG_SZ: self.reg_conn.GetStringValue,
            winreg.REG_DWORD: self.reg_conn.GetDWORDValue,
            winreg.REG_QWORD: self.reg_conn.GetQWORDValue
        }
        self.username = self.get_username_by_sid_dict()
        self.paths = dict()

    def get_value(self, path, name, debug=False):
        # FIXME: Can be only base. F.e. "HKLM"
        name = name.lower()
        base, *branches = path.split("\\")
        key_path = "\\".join(branches)
        base_obj = self._get_base_obj(base)

        if (base_obj, key_path) not in self.paths:
            status_code, names, types = self.reg_conn.EnumValues(hDefKey=base_obj,
                                                                 sSubKeyName=key_path)
            names = list(map(lambda x: x.lower(), names))
            self.paths[(base_obj, key_path)] = (status_code, names, types)
        else:
            status_code, names, types = self.paths.get((base_obj, key_path))

        name_map_type = dict(zip(names, types))

        if name.lower() not in names:
            return

        reg_type = name_map_type[name]
        method = self.give_value_method[reg_type]

        # print(base_obj, key_path, name)
        status_code, value = method(hDefKey=base_obj, sSubKeyName=key_path,
                                    sValueName=name)

        return value

    def sub_branches(self, path):
        # FIXME: Can be only base. F.e. "HKLM"
        base, *branches = path.split("\\")
        key_path = "\\".join(branches)
        base_obj = self._get_base_obj(base)

        status_sode, names = self.reg_conn.EnumKey(hDefKey=base_obj, sSubKeyName=key_path)

        return names

    def get_sids_with_path(self, path):
        sids = self.sub_branches("HKU\\")

        result_sids = []

        for sid in sids:
            subbranches = self.sub_branches(f"HKU\\{sid}\\{path}")

            if not subbranches:
                continue
            else:
                if re.match(r"S-\d+-\d+-\d+-\d+", sid):
                    result_sids.append(sid)

        return result_sids

    @staticmethod
    def _get_base_obj(base):
        base_short_to_long = {
            "HKCR": "HKEY_CLASSES_ROOT",
            "HKCU": "HKEY_CURRENT_USER",
            "HKLM": "HKEY_LOCAL_MACHINE",
            "HKCC": "HKEY_CURRENT_CONFIG",
            "HKU": "HKEY_USERS"
        }

        base_long_to_obj = {
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            "HKEY_USERS": winreg.HKEY_USERS
        }

        base = base.upper()

        if base in base_short_to_long:
            return base_long_to_obj[base_short_to_long[base]]
        elif base in base_long_to_obj:
            return base_long_to_obj[base]
        else:
            return

    def get_username_by_sid_dict(self):
        datas = self.wmi_client.query("Select * FROM win32_accountSID")
        users = dict()

        for data in datas:
            p = re.findall(r'Name=\\"(.+?)\\".+Win32_SID.SID=\\"(.+?)\\"', str(data), re.DOTALL)
            if p:
                data_username, data_sid = p[0]
                users[data_sid] = data_username

        return users

    def copy_branch(self, path1, path2):
        self.wmi_client.Win32_Process.Create(CommandLine=f'reg copy "{path1}" "{path2}" /s /f')

    def dele_branch(self, path):
        self.wmi_client.Win32_Process.Create(CommandLine=f'reg delete "{path}" /f')


transport_classes = {
    "registry": RegistryTransport
}


def get_transport(transport_name, **kwargs):
    transport = transport_classes.get(transport_name)(**kwargs)
    return transport
