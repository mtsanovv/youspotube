import os
import sys

# since the source is in a completely different directory, we need to add it to path in order to be able to make mocks
PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, 'src')
sys.path.append(SOURCE_PATH)

import youspotube.constants as constants  # can be imported only after the src path is added to PATH # noqa: E402

os.environ[constants.ENVIRONMENT_VAR_UNIT_TESTING] = '1'
