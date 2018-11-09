"""Class encapsulating a Gazetteer.
   A Gazetteer contains a set of words that of some types
"""
import pandas as pd
class Gazetteer(object):

    def __init__(self, gazetteer_filepath):
        self.gazetteer = dict()
        df = pd.read_csv(gazetteer_filepath)
        for type_, value_ in zip(df["type"], df["value"]):
            self.gazetteer[str(value_)] = str(type_)

        self.max_length_ = None

    def max_length(self):
        if self.max_length_ == None:
            self.max_length_ = max([ len(val.split()) for val in self.gazetteer.keys() ])

        return self.max_length_

    def is_in_gazetteer(self, value):
        b = False
        if self.gazetteer.__contains__(value):
            b = True

        return b

    def gazetteer_type(self, value):
        type_ = "NA"
        if self.is_in_gazetteer(value):
            type_ = self.gazetteer[value]

        return type_

if __name__ == "__main__":
    gazetteer = Gazetteer("./data/Gazetteer/Vietnamese_Gazetteer_Address+Name.csv")
    print("Max length: %d" % gazetteer.max_length())
    print(gazetteer.is_in_gazetteer("hồ chí minh"))
    print(gazetteer.is_in_gazetteer("hồ chí"))

