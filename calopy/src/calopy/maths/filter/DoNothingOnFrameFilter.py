import logging

from calopy.maths.filter.DoNothingOnSeriesFilter import DO_NOTHING
from calopy.maths.filter.Filter import Filter


class DoNothingOnFrameFilter(Filter):

    logger = logging.getLogger(__name__)
    type = DO_NOTHING

    def apply(self, dataFrame):
        print("Do nothing on frame")
        return dataFrame

    def get_parameter_text(self):
        return ""
