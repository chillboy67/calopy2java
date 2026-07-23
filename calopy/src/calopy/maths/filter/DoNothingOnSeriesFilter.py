import logging

from calopy.maths.filter.Filter import Filter

DO_NOTHING = "Do nothing"


class DoNothingOnSeriesFilter(Filter):
    logger = logging.getLogger(__name__)
    type = DO_NOTHING

    def apply(self, series):
        print("Do nothing on series")
        return series

    def get_parameter_text(self):
        return ""
