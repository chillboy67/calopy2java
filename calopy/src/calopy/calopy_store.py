import datetime
import pickle

from calopy.data import CaliDataTse
from calopy.maths.filter.DoNothingOnSeriesFilter import DO_NOTHING, DoNothingOnSeriesFilter
from calopy.maths.filter.GeneralizedAdditiveFilter import GENERALIZED_ADDITIVE, \
                                                          GeneralizedAdditiveFilter
from calopy.maths.filter.RemoveOutlierFilter import REMOVE_OUTLIER
from calopy.maths.filter.RollingWindowGausianFilter import ROLLING_WINDOW_GAUSIAN, \
                                                           RollingWindowGausianFilter
from calopy.maths.filter.RollingWindowMeanFilter import ROLLING_WINDOW, RollingWindowMeanFilter
from calopy.maths.filter.RollingWindowTriangularFilter import ROLLING_WINDOW_TRIANGULAR, \
                                                              RollingWindowTriangularFilter
from calopy.maths.filter.SavgolFilter import SAVGOL, SavgolFilter
from calopy.maths.filter.SingleComponentCosinorFilter import SINGLE_COMPONENT_COSINOR, \
                                                             SingleComponentCosinorFilter
from calopy.maths.filter.UnivariateSplineAutofitFilter import UNVAR_SPLINE_AUTOFIT, \
                                                              UnivarateSplineAutofitFilter
from calopy.maths.filter.UnivariateSplineFilter import UNVAR_SPLINE, UnivariateSpline
from calopy.writer.TseWriter import ARRAY_SEP, DICT_SEP, KEY_VALUE_SEP, STD_DATE_TIME_FORMAT, \
                                    STD_SEP
from calopy.shared_ui.get_git_version import get_git_commit


calopy_session_store = {}

CALOPY_VERSION = get_git_commit()
CALISTORE_VERSION = "1.0.0"

BETWEEN_GROUPS_MEASUREMENT_1 = "between_groups_measurement_no_1"
BETWEEN_GROUPS_MEASUREMENT_2 = "between_groups_measurement_no_2"
BETWEEN_GROUPS_LIGHT_DARK_FILTER = "light_dark_selection"
BETWEEN_GROUPS_FEATURE_FUNC_VAR1 = "feature_func_var1"
BETWEEN_GROUPS_FEATURE_FUNC_VAR2 = "feature_func_var2"
BETWEEN_GROUPS_GROUPING_1 = "between_groups_grouped"
BETWEEN_GROUPS_GROUPING_2 = "between_groups_2way_factor"
BETWEEN_GROUPS_USE_WELCH = "use_welch"
BETWEEN_GROUPS_USE_2WAY_ANOVA = "use_2wayfactor"
BETWEEN_GROUPS_COMPARE_LIGHT_DARK = "between_groups_night_and_day"
BETWEEN_GROUPS_USE_COVARIATE = "use_covariable"

CONDITIONS_MEASUREMENT = "conditions_measurement"
CONDITIONS_GROUPED = "conditions_grouped"
CONDITIONS_CONDITIONS = "conditions"
CONDITIONS_FEATURE = "conditions_feature"

WINDOW_MEASUREMENT_NO_1 = "window_measurement_no_1"
WINDOW_SWARMPLOT = "window_swarmplot"
WINDOW_STAT_ANNOTATIONS = "window_stat_annotations"
WINDOW_DAY_NIGHT_RESTRICTIONS = "window_day_night_restrictions"
WINDOW_SIZE = "window_size"
WINDOW_TIME_STEPS_MOVED_BY = "window_time_steps_moved_by"
WINDOW_OVERLAPPING_WINDOWS = "overlapping_windows"

ENERGY_BALANCE_EE = "energy_balance_energy_expenditure"
ENERGY_BALANCE_EI = "energy_balance_energy_intake"
ENERGY_BALANCE_GROUPS = "energy_balance_grouped"
ENERGY_BALANCE_COVARIABLE = "energy_balance_covariable"

# SCATTER_GROUPED = "scatter_grouped"
# SCATTER_MEASUREMENT_NO_1 = "scatter_measurement_no_1"
# SCATTER_MEASUREMENT_NO_2 = "scatter_measurement_no_2"
# SCATTER_DAYSPLIT = "scatter_daysplit"
# SCATTER_START = "scatter_start"
# SCATTER_FEATURE_NO_1 = "scatter_feature_no_1"
# SCATTER_FEATURE_NO_2 = "scatter_feature_no_2"
#
# BOX_MEASUREMENT_NO_1 = "box_measurement_no_1"
# BOX_FEATURE = "box_feature"
# BOX_SPLIT_DAY_NIGHT = "box_split_day_night"
# BOX_SWARMPLOT = "box_swarmplot"
# BOX_STAT_ANNOTATIONS = "box_stat_annotations"







def caliData(session):
    ret_data = None
    try:
        ret_data = calopyStore(session).caliData
    except Exception as e:
        pass
    return ret_data


def calopyStore(session):
    if session.id not in calopy_session_store:
        addCaliDataToStore(session, CaliDataTse())
    return calopy_session_store[session.id]


def caliState(session):
    ret_data = None
    try:
        ret_data = calopyStore(session).caliState
    except Exception as e:
        pass
    return ret_data


def addCaliDataToStore(session, data: CaliDataTse, state: dict):
    print("addCaliDataToStore")
    try:
        calopy_session_store[session.id] = CaliStore(data)
        if state is not None:
            try:
                calopy_session_store[session.id].setTseFilter(state["tseFilter"])
                calopy_session_store[session.id].setTseState(state["tseState"])
                calopy_session_store[session.id].setCaliState(state["caliState"])
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
        pass


def downloadCaliStoreObject(session, buf):
    try:
        pickle.dump(calopyStore(session), buf)
    except Exception as e:
        pass

def loadCaliStoreObject(session, caliStorePath):
    try:
        with open(caliStorePath, "rb") as f:
            caliobj = pickle.load(f)  
        if caliobj.caliStoreVersion == CALISTORE_VERSION:
            calopy_session_store[session.id] = caliobj
        else:
            print("calopy store version does not fit: uploaded "+caliobj.caliStoreVersion+" but version should be "+CALISTORE_VERSION)
    except Exception as e:
        pass



class CaliStore:
    def __init__(self, data: CaliDataTse):
        print(f"CaliStore")
        self.calopyVersion = CALOPY_VERSION
        self.caliStoreVersion = CALISTORE_VERSION
        
        self.additionalData = data.additionalData
        self.caliData = data
        self.caliState = {}
        self.initState()

    def setCaliState(self, caliState: dict):
        print("setCaliState")
        for key, typeAndValue in caliState.items():
            type = typeAndValue[0]
            value = typeAndValue[1]
            print(f"load caliState: {key}")
            self.caliState[key] = self.turnToType(type, value)

    def turnToType(self, type, value):
        print(f"turnToType: {type} : {value}")
        if type == "NoneType":
            return None
        elif type == "bool":
            return value == "True"
        elif type == "int":
            return int(value)
        elif type == "float":
            return float(value)
        elif type == "Timestamp" or type == "datetime":
            return datetime.datetime.strptime(value, STD_DATE_TIME_FORMAT)
        elif type == "str":
            return value
        elif type == "list":
            result = []
            valueAsArray = value.split(ARRAY_SEP)
            for item in valueAsArray:
                type, value = item.split(STD_SEP, 1)
                result.append(self.turnToType(type, value))
            return result
        elif type == "dict":
            result = {}
            valueAsArray = value.split(DICT_SEP)
            for item in valueAsArray:
                key, value = item.split(KEY_VALUE_SEP)
                result[key] = self.turnToType(
                    value.split(STD_SEP, 1)[0], value.split(STD_SEP, 1)[1]
                )
            return result

    def setTseState(self, tseState: dict):
        print("setTseState")
        for key, value in tseState.items():
            print(f"load tseState: {key} : {value}")
            if "excludedSamples" == key:
                excludedSamples = value.split(",")
                self.caliData.excludedSamples = list(
                    filter(lambda item: item != "", excludedSamples)
                )
            elif "croppedStart" == key:
                self.caliData.croppedStart = datetime.datetime.strptime(
                    value, STD_DATE_TIME_FORMAT
                )
            elif "croppedEnd" == key:
                self.caliData.croppedEnd = datetime.datetime.strptime(value, STD_DATE_TIME_FORMAT)
            elif "night" == key:
                self.caliData.night = datetime.datetime.strptime(value, "%H:%M").time()
            elif "day" == key:
                self.caliData.day = datetime.datetime.strptime(value, "%H:%M").time()
            elif "groupedBy" == key:
                self.caliData.groupedBy = value
            elif "allSameDayStart" == key:
                self.caliData.allSameDayStart = value
            elif "plotXlabelDay" == key:
                self.caliData.plotXlabelDay = value

    def setTseFilter(self, tseFilter: dict):
        print("setTseFilter")
        for currMeasurement, value in tseFilter.items():
            type = value[0]
            param = value[1]
            outlierFunc = value[2]
            outlierDev = value[3]
            print(
                f"load Filter: {currMeasurement}, {type} : {param} : {outlierFunc} : {outlierDev}"
            )
            if outlierFunc == DO_NOTHING:
                self.caliData.filter.applyOutlierFunc(currMeasurement, False, 0)
            if outlierFunc == REMOVE_OUTLIER:
                self.caliData.filter.applyOutlierFunc(
                    currMeasurement, True, self.getParamValue(outlierDev)
                )
            if type == DO_NOTHING:
                self.caliData.filter.setSmoothing(currMeasurement, DoNothingOnSeriesFilter())
            if type == GENERALIZED_ADDITIVE:
                self.caliData.filter.setSmoothing(currMeasurement, GeneralizedAdditiveFilter())
            if type == ROLLING_WINDOW:
                self.caliData.filter.setSmoothing(
                    currMeasurement, RollingWindowMeanFilter(self.getParamValue(param))
                )
            if type == UNVAR_SPLINE:
                self.caliData.filter.setSmoothing(
                    currMeasurement, UnivariateSpline(self.getParamValue(param))
                )
            if type == ROLLING_WINDOW_TRIANGULAR:
                self.caliData.filter.setSmoothing(
                    currMeasurement,
                    RollingWindowTriangularFilter(self.getParamValue(param)),
                )
            if type == ROLLING_WINDOW_GAUSIAN:
                parameters = param.split(",")
                self.caliData.filter.setSmoothing(
                    currMeasurement,
                    RollingWindowGausianFilter(
                        self.getParamValue(parameters[0]),
                        self.getParamValue(parameters[1]),
                    ),
                )
            if type == UNVAR_SPLINE_AUTOFIT:
                self.caliData.filter.setSmoothing(currMeasurement, UnivarateSplineAutofitFilter())
            if type == SAVGOL:
                parameters = param.split(",")
                self.caliData.filter.setSmoothing(
                    currMeasurement,
                    SavgolFilter(
                        self.getParamValue(parameters[0]),
                        self.getParamValue(parameters[1]),
                    ),
                )
            if type == SINGLE_COMPONENT_COSINOR:
                self.caliData.filter.setSmoothing(
                    currMeasurement,
                    SingleComponentCosinorFilter(self.caliData.timestepsPerDay()),
                )

    def getParamValue(self, param):
        return int(param.split(":")[1])

    def initState(self):
        print("initState")

        self.caliState[BETWEEN_GROUPS_MEASUREMENT_1] = None
        self.caliState[BETWEEN_GROUPS_MEASUREMENT_2] = None
        self.caliState[BETWEEN_GROUPS_LIGHT_DARK_FILTER] = None
        self.caliState[BETWEEN_GROUPS_FEATURE_FUNC_VAR1] = None
        self.caliState[BETWEEN_GROUPS_FEATURE_FUNC_VAR2] = None
        self.caliState[BETWEEN_GROUPS_GROUPING_1] = None
        self.caliState[BETWEEN_GROUPS_GROUPING_2] = None

        self.caliState[BETWEEN_GROUPS_USE_WELCH] = None
        self.caliState[BETWEEN_GROUPS_USE_2WAY_ANOVA] = None
        self.caliState[BETWEEN_GROUPS_COMPARE_LIGHT_DARK] = None
        self.caliState[BETWEEN_GROUPS_USE_COVARIATE] = None

        self.caliState[CONDITIONS_MEASUREMENT] = None
        self.caliState[CONDITIONS_FEATURE] = None
        self.caliState[CONDITIONS_GROUPED] = None
        self.caliState[CONDITIONS_CONDITIONS] = []

        self.caliState[WINDOW_MEASUREMENT_NO_1] = None
        self.caliState[WINDOW_SIZE] = None
        self.caliState[WINDOW_TIME_STEPS_MOVED_BY] = None
        self.caliState[WINDOW_OVERLAPPING_WINDOWS] = None
        self.caliState[WINDOW_SWARMPLOT] = False
        self.caliState[WINDOW_STAT_ANNOTATIONS] = False
        self.caliState[WINDOW_DAY_NIGHT_RESTRICTIONS] = None

        self.caliState[ENERGY_BALANCE_EE] = None
        self.caliState[ENERGY_BALANCE_EI] = None
        self.caliState[ENERGY_BALANCE_GROUPS] = None
        self.caliState[ENERGY_BALANCE_COVARIABLE] = None

        # self.caliState[SCATTER_GROUPED] = None
        # self.caliState[SCATTER_MEASUREMENT_NO_1] = None
        # self.caliState[SCATTER_MEASUREMENT_NO_2] = None
        # self.caliState[SCATTER_DAYSPLIT] = False
        # self.caliState[SCATTER_START] = self.caliData.data.index[0]
        # self.caliState[SCATTER_FEATURE_NO_1] = None
        # self.caliState[SCATTER_FEATURE_NO_2] = None

        # self.caliState[BOX_MEASUREMENT_NO_1] = None
        # self.caliState[BOX_FEATURE] = None
        # self.caliState[BOX_SPLIT_DAY_NIGHT] = False
        # self.caliState[BOX_SWARMPLOT] = False
        # self.caliState[BOX_STAT_ANNOTATIONS] = False




