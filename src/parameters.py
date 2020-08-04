from table import Table


class Parameters(Frame):

    def __init__(self, table):
        super().__init__(isWidthFixed=False, isHeightFixed=False)
        self.columns = table.data.columns


if __name__ == '__main__':
    table = Table.readCSV("examples/animal.csv")
    p = Parameters(table)
    print(p.columns)
