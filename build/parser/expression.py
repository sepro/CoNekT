import csv


class Parser:
    def __init__(self):
        self.profiles = {}
        self.conditions = []
        self.probe_list = {}

    def read_plot(self, plotfile, conversion):
        """
        Reads a plot file and a converts the probe IDs to plots

        :param plotfile: path to the Plot File
        :param conversion: Path to conversion file (for probe IDs to gene IDs)
        """
        with open(conversion) as f:
            for line in f:
                parts = line.strip().split('\t')
                self.probe_list[parts[0]] = parts[1]

        with open(plotfile) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            headers = next(reader, None)
            headers.pop(0)
            self.conditions = headers
            for row in reader:
                probe_id = row.pop(0)
                expr_values = [x.strip('-').split('-') for x in row]

                float_values = []
                for condition in expr_values:
                    float_values.append([float(x) for x in condition])

                probe_data = dict(zip(headers, float_values))
                self.profiles[probe_id] = probe_data

