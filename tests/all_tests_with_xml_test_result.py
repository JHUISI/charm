from all_tests import get_suites
import xmlrunner
xmlrunner.XMLTestRunner(output="test-reports").run(get_suites())
