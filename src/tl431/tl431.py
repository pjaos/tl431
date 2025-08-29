import argparse
import texttable

class RSeries():
    """@brief A representation of various resistor series."""
    # A minimal set of resistor values often sold in resistor kits.
    DEFAULT_SERIES = [0, 100, 120, 150, 220, 330, 470, 680]

    # standard resistor values series
    E12_SERIES = [0, 100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820]
    E24_SERIES = [0, 100, 110, 120, 130, 150, 160, 180, 200, 220, 240, 270, 300,
                330, 360, 390, 430, 470, 510, 560, 620, 680, 750, 820, 910]
    E48_SERIES = [0, 100, 105, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169,
                178, 187, 196, 205, 215, 226, 237, 249, 261, 274, 287, 301,
                316, 332, 348, 365, 383, 402, 422, 442, 464, 487, 511, 536,
                562, 590, 619, 649, 681, 715, 750, 787, 825, 866, 909, 953]
    E96_SERIES = [0, 100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130,
                133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174,
                178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232,
                237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309,
                316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412,
                422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549,
                562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732,
                750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976]
    E192_SERIES = [0, 100, 101, 102, 104, 105, 106, 107, 109, 110, 111, 113, 114,
                115, 117, 118, 120, 121, 123, 124, 126, 127, 129, 130, 132,
                133, 135, 137, 138, 140, 142, 143, 145, 147, 149, 150, 152,
                154, 156, 158, 160, 162, 164, 165, 167, 169, 172, 174, 176,
                178, 180, 182, 184, 187, 189, 191, 193, 196, 198, 200, 203,
                205, 208, 210, 213, 215, 218, 221, 223, 226, 229, 232, 234,
                237, 240, 243, 246, 249, 252, 255, 258, 261, 264, 267, 271,
                274, 277, 280, 284, 287, 291, 294, 298, 301, 305, 309, 312,
                316, 320, 324, 328, 332, 336, 340, 344, 348, 352, 357, 361,
                365, 370, 374, 379, 383, 388, 392, 397, 402, 407, 412, 417,
                422, 427, 432, 437, 442, 448, 453, 459, 464, 470, 475, 481,
                487, 493, 499, 505, 511, 517, 523, 530, 536, 542, 549, 556,
                562, 569, 576, 583, 590, 597, 604, 612, 619, 626, 634, 642,
                649, 657, 665, 673, 681, 690, 698, 706, 715, 723, 732, 741,
                750, 759, 768, 777, 787, 796, 806, 816, 825, 835, 845, 856,
                866, 876, 887, 898, 909, 920, 931, 942, 953, 965, 976, 988]

    @staticmethod
    def GetSeries(series_name):
        series = None
        if series_name.lower() == 'default':
            series = RSeries.DEFAULT_SERIES

        elif series_name.lower() == 'e192':
            series = RSeries.E192_SERIES

        elif series_name.lower() == 'e96':
            series = RSeries.E96_SERIES

        elif series_name.lower() == 'e48':
            series = RSeries.E48_SERIES

        elif series_name.lower() == 'e12':
            series = RSeries.E12_SERIES

        elif series_name.lower() == 'e24':
            series = RSeries.E24_SERIES

        else:
            raise Exception(f"{series_name} is an unknown series.")

        return series


class TL431():
    """@brief Responsible for calculating the resistor values to be used with a TL431 device.

    - Filters out the silly low-ohm solutions.
    - Keeps divider current under 1 mA.
    - Ensures TL431 Ik stays between 1–20 mA.
    - Ensures Rs current ≤ 10 mA.
    - Returns the n best matches."""

    SCHEMATIC = '''
    VIN -- Rs ----------- VOUT
            |       |
            R1      |
            |       K
            |---R TL431
            |       A
            R2      |
            |       |
    GND ----------------- GND
    '''

    VREF = 2.495  # TL431 reference voltage
    I_REF = 2e-6  # TL431 ref input current (typical)

    def show_schematic(self):
        print('')
        print('Schematic')
        print(TL431.SCHEMATIC)

    def check_voltages(self, vin, vout):

        if vin < TL431.VREF:
            raise Exception(f"Vin must be at least {TL431.VREF}V.")

        if vout < TL431.VREF:
            raise Exception(f"Vout must be at least {TL431.VREF}V.")

    def _make_resistor_series(self, series, decades=7):
        values = []
        for d in range(decades):
            mul = 10 ** d
            values.extend([base * mul for base in series])
        return sorted(values)

    def _calc_vout(self, R1, R2):
        return TL431.VREF * (1 + R1 / R2)

    def _find_solutions(self, Vin, Vout_target, series,
                    Ik_min=1e-3, Ik_max=20e-3,
                    Idiv_max=1e-3, Irs_max=10e-3,
                    max_results=10):
        values = self._make_resistor_series(series)
        best = []

        for R2 in values:
            for R1 in values:
                # PJA, skip zero Ω resistors and -ve values
                if R2 <= 0 or R1 <= 0:
                    continue
                vout = self._calc_vout(R1, R2)
                error = abs(vout - Vout_target)

                # divider current
                Idiv = vout / (R1 + R2)

                if Idiv > Idiv_max:
                    continue  # too much divider current

                for Rs in values:
                    # PJA, skip zero Ω resistors and -ve values
                    if Rs <= 0:
                        continue
                    Irs = (Vin - vout) / Rs
                    Ik = Irs - Idiv

                    if Ik < Ik_min or Ik > Ik_max:
                        continue  # TL431 out of spec
                    if Irs > Irs_max:
                        continue  # too much series current

                    best.append((error, vout, R1, R2, Rs, Idiv, Irs, Ik))

        # sort by error, then by lowest Rs current
        best.sort(key=lambda x: (x[0], x[6]))

        return best[:max_results]

    def _show_table(self, solutions, Vout_target):
        """Print a pretty table using texttable module"""
        table = texttable.Texttable()
        table.set_cols_width([8, 14, 6, 9, 9, 7, 8, 7])
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_dtype(['t', 't', 't', 't', 't', 't', 't', 't'])
        table.set_cols_align(['r', 'r', 'r', 'r', 'r', 'r', 'r', 't'])

        output_table = []
        output_table.append(['VOUT V','VOUT Err V/%' ,'Rs Ω'    ,'R1 Ω'    ,'R2 Ω'    ,'RS I mA','Divider I mA','TL431 Ik mA'])
        for i, (error, vout, R1, R2, Rs, Idiv, Irs, Ik) in enumerate(solutions, 1):
            output_table.append([f'{vout:.6f}',
                                 f'{error:.6f}/{(error / Vout_target) * 100:.3f}',
                                 f'{Rs}',
                                 f'{R1}',
                                 f'{R2}',
                                 f'{Irs*1e3:.3f}',
                                 f'{Idiv*1e3:.6f}',
                                 f'{Ik*1e3:.3f}'])
        table.add_rows(output_table)
        print(table.draw())

    def calc(self, Vin, Vout_target, series, Ik_min = 1E-3, Idiv_max=1e-3):
        self.show_schematic()

        solutions = self._find_solutions(Vin, Vout_target, series, Ik_min=Ik_min, Idiv_max=Idiv_max)

        self._show_table(solutions, Vout_target)

        print('')
        print(f"VIN:         {Vin:.3f} V")
        print(f"VOUT Target: {Vout_target:.3f} V")
        print('')

def main():
    """@brief Program entry point"""

    try:
        parser = argparse.ArgumentParser(description="Calculate TL431 resistor divider + series resistor values for target Vout.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('--vin', type=float, help='The minimum input voltage (V)')
        parser.add_argument('--vout', type=float, help='Required output voltage (V)')
        parser.add_argument('-s', dest='e_series', type=str, default='default', \
                choices=['default', 'e12', 'e24', 'e48', 'e96', 'e192'], \
                help='E series')
        parser.add_argument("-d", "--debug",  action='store_true', help="Enable debugging.")

        options = parser.parse_args()
        if options.e_series == 'e96' or options.e_series == 'e192':
            raise Exception(f'{options.e_series} series resistors take to long and to much CPU to process.')

        tl431 = TL431()
        tl431.check_voltages(options.vin, options.vout)
        r_series = RSeries.GetSeries(options.e_series)
        tl431.calc(options.vin, options.vout, r_series)

    # If the program throws a system exit exception
    except SystemExit:
        pass
    # Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:

        if options.debug:
            raise
        else:
            print(str(ex))


if __name__ == '__main__':
    main()
