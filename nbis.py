import configuration
from pathlib import Path
import subprocess
import re

config = configuration.load()
nbis_path = Path(config['nbis']['bin'])
tmp_path = Path(config['tmp'])


def write_out(file: str, content: str) -> None:
    file_h = Path.open(Path(file), 'w')
    file_h.write(content)
    file_h.close()


def get_nfiq_quality(image_file: Path) -> int:
    return int(subprocess.run([str(nbis_path / 'nfiq'), str(image_file)], stdout=subprocess.PIPE,
                              cwd=tmp_path).stdout.decode())


def get_classification(image_file: Path) -> (str, float):
    image_txt_file = ('../' * 10) + str(image_file) + '.txt'
    image_prs_file = (str(image_file) + '.prs')
    write_out(image_txt_file, ('../' * 10) + str(image_file) + ' S')
    write_out(image_prs_file,
              "demo_images_list %s\n" % image_txt_file +
              "outfile /dev/null\n"
              "clobber_outfile y\n"
              "verbose y\n")
    output = subprocess.run([str(nbis_path / 'pcasys'), image_prs_file], stdout=subprocess.PIPE).stdout.decode()
    matches = re.search(r'is [WSLRTA]; nn: hyp [WSLRTA], conf [0-1]\.[0-9][0-9]; conup [yn]; hyp ([WSLRTA]), conf ([0-1]\.[0-9][0-9])', output)
    return matches.group(1).lower(), float(matches.group(2))


def generate_mindtct_templates(image_file: Path, out_root: Path) -> None:
    subprocess.run([str(nbis_path / 'mindtct'), str(image_file), str(out_root)], stdout=subprocess.PIPE)


def get_bozorth3_score(xyt_file_a: Path, xyt_file_b: Path) -> int:
    try:
        result = int(subprocess.run([str(nbis_path / 'bozorth3'), str(xyt_file_a), str(xyt_file_b)],
                              stdout=subprocess.PIPE).stdout.decode())
    except:  # In general this will only fail if there is a programming error or the template itself is invalid
        return 0
    return result
