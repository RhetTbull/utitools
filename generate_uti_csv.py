"""Generate uti.csv for use by utitools; this script may take a long time to run!"""

import csv
import itertools
import string

from utitools import preferred_suffix_for_uti, uti_for_suffix

MAX_SUFFIX_LEN = 6

def generate_csv_data():
    characters = string.ascii_lowercase + string.digits

    fd = open("uti.csv", "w")
    csv_writer = csv.writer(fd)
    csv_writer.writerow(["extension", "UTI", "preferred_extension"])

    for length in range(1, MAX_SUFFIX_LEN+1):
        for combination in itertools.product(characters, repeat=length):
            suffix = "".join(combination)
            status = f" checking {suffix}".ljust(MAX_SUFFIX_LEN+10)
            print(status, end="\r")
            uti = uti_for_suffix(suffix)
            if not uti:
                continue
            preferred_suffix = preferred_suffix_for_uti(uti)
            if preferred_suffix:
                preferred_suffix = preferred_suffix[1:]
            print(",".join([suffix, uti, preferred_suffix]))
            csv_writer.writerow([suffix, uti, preferred_suffix])
            fd.flush()
    fd.close()

if __name__ == "__main__":
    generate_csv_data()
