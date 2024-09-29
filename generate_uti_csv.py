"""Generate uti.csv for use by utitools"""

import csv
import itertools
import string

from utitools import preferred_suffix_for_uti, uti_for_suffix


def generate_csv_data():
    letters = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'

    fd = open("uti.csv", "w")
    csv_writer = csv.writer(fd)
    csv_writer.writerow(["extension", "UTI", "preferred_extension"])

    # Generate combinations for length 1 to 6
    for length in range(1, 7):
        for combination in itertools.product(letters, repeat=length):
            suffix = "".join(combination)
            uti = uti_for_suffix(suffix)
            if not uti:
                continue
            preferred_suffix = preferred_suffix_for_uti(uti)
            if preferred_suffix:
                preferred_suffix = preferred_suffix[1:]
            print(",".join([suffix, uti, preferred_suffix]))
            csv_writer.writerow([suffix, uti, preferred_suffix])
    fd.close()

if __name__ == "__main__":
    generate_csv_data()
