import unittest
from sys import platform
from aer_inibitor import PCI_EXP_DEVCTL, PCIID_REGEX, PCIADD_REGEX, get_setpci_base_command, get_setpci_read_command, get_setpci_write_command, get_AER_type_index, AER_TYPES_MAP


class TestAERInibitor(unittest.TestCase):

    def test_constants(self):
        self.assertEqual(PCI_EXP_DEVCTL, 8)

    def test_PCIID_regex(self):
        self.assertIsNotNone(PCIID_REGEX.match("10de:1000"))

        self.assertIsNone(PCIID_REGEX.match("10def:1000"))
        self.assertIsNone(PCIID_REGEX.match("10e:1000"))
        self.assertIsNone(PCIID_REGEX.match("10ez:1000"))

        self.assertIsNone(PCIID_REGEX.match("10de:1000f"))
        self.assertIsNone(PCIID_REGEX.match("10de:100"))
        self.assertIsNone(PCIID_REGEX.match("10e:100z"))

    def test_PCADD_regex(self):
        self.assertIsNotNone(PCIADD_REGEX.match("c4:00.2"))
        self.assertIsNotNone(PCIADD_REGEX.match("4:00.2"))
        self.assertIsNotNone(PCIADD_REGEX.match("c4:00.22"))
        self.assertIsNotNone(PCIADD_REGEX.match("0000:c4:00.22"))
        self.assertIsNotNone(PCIADD_REGEX.match("0001:c4:00.22"))
        self.assertIsNotNone(PCIADD_REGEX.match("9999:c4:00.22"))

        self.assertIsNone(PCIADD_REGEX.match("c4:z0.2"))
        self.assertIsNone(PCIADD_REGEX.match("z4:00.22"))
        self.assertIsNone(PCIADD_REGEX.match("c4:00.224"))
        self.assertIsNone(PCIADD_REGEX.match("000z:c4:00.22"))

    def test_setpci_base_commands(self):
        self.assertEqual(get_setpci_base_command(
            pciid="10de:1401"), "setpci -v -d 10de:1401 CAP_EXP+0x8.w")
        self.assertEqual(get_setpci_base_command(
            pci_address="0000:c4:00.2"), 'setpci -v -s "0000:c4:00.2" CAP_EXP+0x8.w')
        self.assertEqual(get_setpci_base_command(pciid="10de:1401",
                                                 pci_address="0000:c4:00.2"),
                         'setpci -v -d 10de:1401 -s "0000:c4:00.2" CAP_EXP+0x8.w')

        # Raise Exception if arguments are not enough
        self.assertRaises(Exception, get_setpci_base_command, None, None)
        self.assertRaises(Exception, get_setpci_base_command,
                          None, pciid="z:213863")
        self.assertRaises(Exception, get_setpci_base_command,
                          None, pci_address="000z:c4:00.22")

    def test_setpci_read_commands(self):
        self.assertEqual(get_setpci_base_command(pciid="10de:1401"),
                         get_setpci_read_command(pciid="10de:1401"))
        self.assertEqual(get_setpci_base_command(pci_address="0000:c4:00.2"),
                         get_setpci_read_command(pci_address="0000:c4:00.2"))
        self.assertEqual(get_setpci_base_command(pciid="10de:1401",
                                                 pci_address="0000:c4:00.2"),
                         get_setpci_read_command(pciid="10de:1401",
                                                 pci_address="0000:c4:00.2"))

    def test_setpci_write_commands(self):
        values = ["0xabcde", "ABCDEF", "1f2a3", "0x1f2a3"]
        for value in values:
            exp_value = f"0x{value.lower().replace('0x','')}"
            self.assertEqual(get_setpci_base_command(pciid="10de:1401")+f"={exp_value}",
                             get_setpci_write_command(pciid="10de:1401",
                                                      value=value))
            self.assertEqual(get_setpci_base_command(pci_address="0000:c4:00.2")+f"={exp_value}",
                             get_setpci_write_command(pci_address="0000:c4:00.2",
                                                      value=value))
            self.assertEqual(get_setpci_base_command(pciid="10de:1401",
                                                     pci_address="0000:c4:00.2")+f"={exp_value}",
                             get_setpci_write_command(pciid="10de:1401",
                                                      pci_address="0000:c4:00.2",
                                                      value=value))
    def test_get_AER_type_index(self):
        self.assertRaises(Exception, get_AER_type_index, "thisdoesntexist")

        self.assertEqual(AER_TYPES_MAP['corrected'][0], 1)
        self.assertEqual(AER_TYPES_MAP['nonfatal'][0], 2)
        self.assertEqual(AER_TYPES_MAP['fatal'][0], 3)
        self.assertEqual(AER_TYPES_MAP['unsupported'][0], 4)

        self.assertEqual(get_AER_type_index('corrected'), 1)
        self.assertEqual(get_AER_type_index('nonfatal'), 2)
        self.assertEqual(get_AER_type_index('fatal'), 3)
        self.assertEqual(get_AER_type_index('unsupported'), 4)


if __name__ == '__main__':
    unittest.main()
