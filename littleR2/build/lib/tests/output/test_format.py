from unittest import TestCase

from littler.output.format import LittleRFormatter, _Record, _Header, _Report
from littler.level import Level, DEFAULT_FLOAT

from tests.utils import get_data_filename


# Taken from http://www2.mmm.ucar.edu/wrf/users/wrfda/OnlineTutorial/Help/littler.html
HEADER_VALS = [
    [
        39.78000, -104.86000, '72469', 'DENVER/STAPLETON INT., CO. / U.S.A.',
        'FM-35 TEMP', 'GTS (ROHK) UKUS09 KWBC 051200 RRA', 1626.00000, 890,
        True, False, '20080205120000', -888888.0, -888888.0
     ],
    [
        -71.86300, -125.59700, '-7777', 'Platform Id >>> 71656', 'FM-18 BUOY',
        'GTS (ROHK) SSVX07 LFVW 051100', 0.00000, 564,
        False, False, '20080205110000', 97940.0, 97940.0
     ]
]

LEVELS = [
    [
        [83500.0, -888888.0, 264.44998, 263.35001, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [72100.0, -888888.0, 257.85001, 256.14999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [59100.0, -888888.0, 252.45000, 250.34999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [46600.0, -888888.0, 241.84999, 239.34999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [40000.0, -888888.0, 232.84999, 229.75000, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [37200.0, -888888.0, 229.84999, 223.84999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [33900.0, -888888.0, 228.04999, 214.04999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [25400.0, -888888.0, 226.45000, 202.45000, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [23300.0, -888888.0, 229.45000, 201.45000, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [14100.0, -888888.0, 220.64999, 195.64999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0],
        [10000.0, -888888.0, 218.64999, 194.64999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0]
    ],
    [
        [97940.00000, 0.0, 272.04999, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.0, -888888.00000]
    ]
]


class TestFormat(TestCase):

    def test_LittleRFormatter_start_new_report(self):
        fmtr = LittleRFormatter()

        fmtr.start_new_report()
        fmtr.start_new_report(_get_levels(0))
        fmtr.start_new_report()

        self.assertEqual(len(fmtr.reports), 3)
        self.assertEqual(len(fmtr.reports[0].records), 0)
        self.assertEqual(len(fmtr.reports[1].records), len(LEVELS[0]))
        self.assertEqual(len(fmtr.reports[2].records), 0)

    def test_LittleRFormatter_add_level_error(self):
        # Make sure that the formatter fails if a report hasn't been started
        fmtr = LittleRFormatter()

        self.assertRaises(IndexError, fmtr.add_level, Level())

        fmtr.start_new_report()
        try:
            fmtr.add_level(Level())
        except IndexError:
            self.fail('add_level raised an unexpected error.')

    def test_LittleRFormatter_add_level(self):
        testlv1 = Level()
        testlv1.height = (0.0, 0)
        testlv2 = Level()
        testlv2.height = (1.0, 0)
        out = LittleRFormatter()

        out.start_new_report()
        out.add_level(testlv1)
        out.start_new_report()
        out.add_level(testlv2)
        # Make sure that add_level adds the levels to the appropriate reports
        self.assertNotEqual(out.reports[0].records[0].lv, out.reports[1].records[0].lv)
        self.assertNotEqual(str(out.reports[0].records[0]), str(out.reports[1].records[0]))

    def test_LittleRFormatter_no_reports(self):
        fmtr = LittleRFormatter()
        fmtr.start_new_report()
        result = fmtr.format()

        with open(get_data_filename('ExampleEmptyReport.txt')) as fd:
            expected = fd.read()
        self.assertEqual(result, expected)

    def test_LittleRFormatter_format_single_report(self):
        fmtr = LittleRFormatter()

        fmtr.start_new_report(_get_levels(0))
        result = fmtr.format()

        with open(get_data_filename('ExampleReport.txt')) as fd:
            expected_out = fd.read()
        self.assertEqual(result, expected_out)

    def test_LittleRFormatter_format_multiple_reports(self):
        fmtr = LittleRFormatter()

        fmtr.start_new_report(_get_levels(0))
        fmtr.start_new_report(_get_levels(1))
        result = fmtr.format()

        with open(get_data_filename('ExampleMultipleReports.txt')) as fd:
            expected_out = fd.read()
        self.assertEqual(result, expected_out)

    def test_recordStr(self):
        # Test default
        rec = _Record(Level())

        expected_str = '-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'
        self.assertEqual(str(rec), expected_str, "Default Record str must match expected")

        # Test with specific values
        lv = Level()
        lv.pres = (83500.00000, 0)
        lv.temp = (264.44998, 0)
        lv.dewpoint = (263.35001, 0)
        rec = _Record(lv)

        expected_str = '  83500.00000      0-888888.00000      0    264.44998      0    263.35001      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'
        self.assertEqual(str(rec), expected_str, "Record str must match expected")

    def test_headerStr(self):
        lv = Level()
        _set_header_vals(HEADER_VALS[0], lv)
        lv.valid_fields = 1
        header = _Header(lv, lv.valid_fields)

        expected_str = '            39.78000          -104.8600072469                                   DENVER/STAPLETON INT., CO. / U.S.A.     FM-35 TEMP                              GTS (ROHK) UKUS09 KWBC 051200 RRA                 1626.00000         1   -888888   -888888       890   -888888         T         F         F   -888888   -888888      20080205120000-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'
        self.assertEqual(str(header), expected_str)

    def test_header_length(self):
        max_len = 600

        lv = Level()
        lv.name = 'A'*100
        lv.id = 'I'*100
        lv.source = 'S'*100

        h = _Header(lv, lv.valid_fields)

        self.assertEqual(len(str(h)), max_len)

    def test_reportStr(self):
        levels = [_vals_to_level(HEADER_VALS[0], lv) for lv in LEVELS[0]]
        rep = _Report()
        rep.add_records(levels)

        with open(get_data_filename('ExampleReport.txt')) as fd:
            expected_str = fd.read()
        self.assertEqual(str(rep), expected_str, 'Report str must match expected')


def _get_levels(i):
    return [_vals_to_level(HEADER_VALS[i], lv) for lv in LEVELS[i]]


def _vals_to_level(hvals, vals):
    lv = Level()
    _set_header_vals(hvals, lv)
    lv.valid_fields = len(vals) - vals.count(DEFAULT_FLOAT)
    lv.pres = (vals[0], 0)
    lv.height = (vals[1], 0)
    lv.temp = (vals[2], 0)
    lv.dewpoint = (vals[3], 0)
    lv.windspd = (vals[4], 0)
    lv.winddir = (vals[5], 0)
    lv.windu = (vals[6], 0)
    lv.windv = (vals[7], 0)
    lv.rh = (vals[8], 0)
    lv.thickness = (vals[9], 0)
    return lv


def _set_header_vals(hvals, lv):
    lv.lat = hvals[0]
    lv.lon = hvals[1]
    lv.id = hvals[2]
    lv.name = hvals[3]
    lv.platform = hvals[4]
    lv.source = hvals[5]
    lv.alt = hvals[6]
    lv.seq_num = hvals[7]
    lv.is_sounding = hvals[8]
    lv.bogus = hvals[9]
    lv.date = hvals[10]
    lv.slp = (hvals[11], 0)
    lv.sfc_pres = (hvals[12], 0)
