#!/usr/local/bin/python3
import sys
import csv


class Config(object):

    def __init__(self, filename):
        self.filename = filename
        self.config_lines = self._get_file_contents(self.filename)
        self.selections = self._get_selections(self.config_lines)
        self.s = self.selections

    def _get_file_contents(self, filename):
        try:
            with open(filename) as file:
                config_lines = file.readlines()
        except FileNotFoundError:
            print('File: ' + filename + ' not found')
            sys.exit()
        return config_lines

    def _get_option(self, line_elements):
        for element in line_elements:
            if 'CONFIG' in element:
                return element
        return None

    def _get_selections(self, config_lines):
        selections = {}
        for line in config_lines:
            line_elements = line.replace('\n', '').split(' ')
            option = self._get_option(line_elements)
            if option:
                if line_elements[0][0] == '#':
                    selections[option] = None
                else:
                    option_elements = option.split('=')
                    selections[option_elements[0]] = option_elements[1]
        return selections

    def keys(self):
        return self.selections.keys()

    def num(self):
        return len(self.selections.keys())

    def in_both(self, comparator):
        return [key for key in self.selections if key in comparator]

    def self_only(self, comparator):
        return [key for key in self.selections if key not in comparator]

    def comparator_only(self, comparator):
        return [key for key in comparator if key not in self.selections]

    def explicit_same_values(self, comparator):
        return [key for key in self.in_both(comparator) if self.selections[key] == comparator[key]]

    def same_values(self, comparator):
        declared_and_same = self.explicit_same_values(comparator)
        only_in_self_and_not_set = [key for key in self.self_only(comparator) if self.selections[key] == None]
        only_comp_and_not_set = [key for key in self.comparator_only(comparator) if comparator[key] == None]
        return declared_and_same + only_in_self_and_not_set + only_comp_and_not_set

    def has_diff_value(self, comparator):
        all_declared = list(set(self.selections) | set(comparator))
        same_values = self.same_values(comparator)
        return [key for key in all_declared if key not in same_values]

    def num_in_both(self, comparator):
        return len(self.in_both(comparator))

    def num_comparator_only(self, comparator):
        return len(self.comparator_only(comparator))

    def num_self_only(self, comparator):
        return len(self.self_only(comparator))

    def num_same_values(self, comparator):
        return len(self.same_values(comparator))

    def num_diff_values(self, comparator):
        return len(self.has_diff_value(comparator))

    def num_total_opts(self, comparator):
        return self.num() + self.num_comparator_only(comparator)


class Table(object):

    def __init__(self, config_a, config_b, user_opts):
        self.a = config_a
        self.b = config_b
        self.user_opts = user_opts
        self.filter = self.get_filter()
        self.diff_table = self._diff_table()

    def get_filter(self):
        for opt in self.user_opts:
            if '-filter' in opt:
                return opt.split('=')[1]
        return None

    def filter_diff(self):
        if self.filter:
            filtered = []
            for line in self.diff_table:
                if self.filter not in line[0]:
                    filtered.append(line)
            return filtered
        return None

    def _diff_table(self):
        table = []
        table.append(['Option', self.a.filename, self.b.filename])
        for key in self.a.has_diff_value(self.b.selections):
            table.append([key, self.a.selections.get(key), self.b.selections.get(key)])
        return table

    def diff_csv(self):
        data = self.filter_diff() if self.filter else self.diff_table
        with open('config_diff.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            for row in data:
                writer.writerow(row)

# def diff_all(self):
# 	self.diff_csv(self.diff_table)

# def diff_filtered(self):
# 	self.diff_csv(self.filter_diff())


def get_targets():
    targets = [arg for arg in sys.argv[1:] if arg[0] != '-']
    if len(targets) < 2:
        print('Not enough arguments')
        sys.exit()
    elif len(targets) > 2:
        print('Too many arguments')
        sys.exit()
    return targets


def get_opts():
    valid_opts = ['-file', '-filter']
    opts = [arg for arg in sys.argv[1:] if arg[0] == '-']
    # for opt in opts:
    # 	if opt not in valid_opts:
    # 		print('Invalid option: ' + opt)
    # 		sys.exit()
    return opts


targets = get_targets()
user_opts = get_opts()

tab = Table(Config(targets[0]), Config(targets[1]), user_opts)

tab.diff_csv()
