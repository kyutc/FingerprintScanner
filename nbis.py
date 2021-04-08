import configuration
from pathlib import Path
import subprocess
import re

config = configuration.load()
nbis_path = Path(config['nbis']['bin'])
tmp_path = Path(config['tmp'])


def write_out(file, content):
    file_h = Path.open(Path(file), 'w')
    file_h.write(content)
    file_h.close()


def get_nfiq_quality(image_file):
    return int(subprocess.run([str(nbis_path / 'nfiq'), str(image_file)], stdout=subprocess.PIPE,
                              cwd=tmp_path).stdout.decode())


def get_classification(image_file):
    image_txt_file = ('../' * 10) + str(image_file) + '.txt'
    image_prs_file = (str(image_file) + '.prs')
    write_out(image_txt_file, ('../' * 10) + str(image_file) + ' S')
    write_out(image_prs_file,
              "demo_images_list %s\n" % image_txt_file +
              "outfile /dev/null\n"
              "clobber_outfile y\n"
              "verbose y\n")
    output = subprocess.run([str(nbis_path / 'pcasys'), image_prs_file], stdout=subprocess.PIPE).stdout.decode()
    #print(output)
    matches = re.search(r'is [WSLRTA]; nn: hyp [WSLRTA], conf [0-1]\.[0-9][0-9]; conup [yn]; hyp ([WSLRTA]), conf ([0-1]\.[0-9][0-9])', output)
    return matches.group(1), float(matches.group(2))


def generate_mindtct_templates(image_file, out_root):
    subprocess.run([str(nbis_path / 'mindtct'), str(image_file), str(out_root)], stdout=subprocess.PIPE)


def get_bozorth3_score(xyt_file_a, xyt_file_b):
    return int(subprocess.run([str(nbis_path / 'bozorth3'), str(xyt_file_a), str(xyt_file_b)],
                              stdout=subprocess.PIPE).stdout.decode())
