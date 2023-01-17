#! 

from os.path import join, dirname
import re
import subprocess
import yaml

HEX_PREFIX_REGEX = re.compile('^0[xX]')
HEX_REGEX = re.compile('^(0[xX])?[0-9a-fA-F]*$')
PCIID_REGEX = re.compile('^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$')
PCIADD_REGEX = re.compile(
    '^([0-9]{0,4}:)?[0-9a-fA-F]{1,2}:[0-9a-fA-F]{2}.[0-9a-fA-F]{1,2}$')

PCI_EXP_DEVCTL = 8             # Default offset from the standard CAP_EXP registry
AER_TYPES_MAP = {}
AER_TYPES_MAP['corrected'] = (1, "Corrected errors")    # Which means 0x0001
AER_TYPES_MAP['nonfatal'] = (2, "Non-fatal errors")     # Which means 0x0002
AER_TYPES_MAP['fatal'] = (3, "Fatal errors")            # Which means 0x0004
AER_TYPES_MAP['unsupported'] = (4, "Unsupported errors")  # Which means 0x0008


def get_setpci_base_command(pciid=None, pci_address=None):
    if not(pciid or pci_address):
        raise Exception(
            "Please provide at least an univocal pciid or pci address.")

    if pciid:
        if not PCIID_REGEX.match(pciid):
            raise Exception(
                f"Provided pciid {pciid} does not match the typical pciid pattern (FFFF:FFFF)")

    if pci_address:
        if not PCIADD_REGEX.match(pci_address):
            raise Exception(
                f"Provided pci address {pci_address} does not match the typical pci address pattern ([FFFF.]FF:FF.FF)")

    pciid_opt = f"-d {pciid}" if pciid else ''
    pci_address_opt = f"-s \"{pci_address}\"" if pci_address else ''
    setpci_command = f"setpci -v {pciid_opt} {pci_address_opt} CAP_EXP+0x{PCI_EXP_DEVCTL}.w".replace('  ',' ')

    return setpci_command


def get_setpci_read_command(pciid=None, pci_address=None):
    return get_setpci_base_command(pciid=pciid, pci_address=pci_address)


def get_setpci_write_command(pciid=None, pci_address=None, value=None):
    if not value:
        raise Exception("Value to write is mandatory")

    if not HEX_REGEX.match(value):
        raise Exception(f"The provided value {value} is not a valid HEX string")

    if not HEX_PREFIX_REGEX.match(value):
        value = f"0x{value}"

    return f"{get_setpci_base_command(pciid=pciid, pci_address=pci_address)}={value.lower()}"


def run_setpci_command(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    if(err):
        raise Exception(f"Command failed with error:/n{err.decode()}")

    return out.decode()


def get_AER_caps(pciid=None, pci_address=None, verbose=False):
    AER_caps_hex = run_setpci_command(get_setpci_read_command(pciid=pciid,
                                                              pci_address=pci_address)
                                      ).split('=')[-1].strip()
    return f"0x{AER_caps_hex}"


def set_AER_caps(pciid=None, pci_address=None, index=None, enable=True):
    AER_cap_flags = get_AER_caps(pciid=pciid, pci_address=pci_address)
    AER_caps_bin = list(bin(int(AER_cap_flags, 0))[2:])
    new_AER_cap_bin = AER_caps_bin
    new_AER_cap_bin[-index] = '1' if enable else '0'

    new_AER_cap_flags = hex(int(''.join(new_AER_cap_bin), 2))

    return run_setpci_command(get_setpci_write_command(pciid=pciid, pci_address=pci_address, value=new_AER_cap_flags))


def get_AER_type_index(type):
    if type not in AER_TYPES_MAP.keys():
        raise Exception(
            f"Provided type {type} is not supported. Valid types are {', '.join(AER_TYPES_MAP.keys())}")
    return AER_TYPES_MAP[type][0]


def enable_AER_type(pciid=None, pci_address=None, type=None):
    return set_AER_caps(pciid=pciid, pci_address=pci_address, index=get_AER_type_index(type=type), enable=True)


def disable_AER_type(pciid=None, pci_address=None, type=None):
    return set_AER_caps(pciid=pciid, pci_address=pci_address, index=get_AER_type_index(type=type), enable=False)


if __name__ == "__main__":
    with open(join(dirname(__file__), 'config.yaml')) as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)
        print(settings)

        for device in settings['devices']:
            pciid = device.get('pciid')
            pci_address = device.get('pci_address')
            for flag in device['flags']:
                if flag['enabled'] == True:
                    enable_AER_type(pciid=pciid, pci_address=pci_address, type=flag['aer_type'])
                elif flag['enabled'] == False:
                    disable_AER_type(pciid=pciid, pci_address=pci_address, type=flag['aer_type'])
