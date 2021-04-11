from pathlib import Path
import subprocess
import re
from util_helper import *


class NBIS:
    nbis_path: Path = None
    nfiq_path: Path = None
    pcasys_path: Path = None
    mindtct_path: Path = None
    bozorth3_path: Path = None

    @classmethod
    def init(cls, nbis_bin_path: Path) -> None:
        cls.nbis_path = nbis_bin_path
        cls.nfiq_path = cls.nbis_path / 'nfiq'
        cls.pcasys_path = cls.nbis_path / 'pcasys'
        cls.mindtct_path = cls.nbis_path / 'mindtct'
        cls.bozorth3_path = cls.nbis_path / 'bozorth3'

    @classmethod
    def get_nfiq_quality(cls, image_file: Path) -> int:
        try:
            return int(subprocess.run([str(cls.nfiq_path), str(image_file)], stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL).stdout.decode())
        except:
            return 100  # Arbitrarily low quality for an error condition

    @classmethod
    def get_classification(cls, image_file: Path) -> (str, float):
        image_txt_file = ('../' * 10) + str(image_file) + '.txt'
        image_prs_file = (str(image_file) + '.prs')
        write_file(Path(image_txt_file), ('../' * 10) + str(image_file) + ' S')
        write_file(Path(image_prs_file),
                   "demo_images_list %s\n" % image_txt_file +
                   "outfile /dev/null\n"
                   "clobber_outfile y\n"
                   "verbose y\n")
        output = subprocess.run([str(cls.pcasys_path), image_prs_file], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL).stdout.decode()
        matches = re.search(
            r'is [WSLRTA]; nn: hyp [WSLRTA], conf [0-1]\.[0-9][0-9]; conup [yn]; hyp ([WSLRTA]), conf ([0-1]\.[0-9][0-9])',
            output)
        return matches.group(1).lower(), float(matches.group(2))

    @classmethod
    def generate_mindtct_templates(cls, image_file: Path, out_root: Path) -> None:
        subprocess.run([str(cls.mindtct_path), str(image_file), str(out_root)], stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL)

    @classmethod
    def get_bozorth3_score(cls, xyt_file_a: Path, xyt_file_b: Path) -> int:
        try:
            result = int(subprocess.run([str(cls.bozorth3_path), str(xyt_file_a), str(xyt_file_b)],
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode())
        except:
            return 0
        return result
