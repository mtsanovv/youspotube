import sys
import youspotube.constants as constants

class Help:
    def print():
        print("\nAvailable options:")
        print("%-20sDisplays this help menu" % constants.HELP_OPTION)
        print("%-20sForces usage of config file" % constants.CONFIG_FILE_OPTION)
        print("\nIn case no options are to be specified, stick to the following usage:")
        print("%s <origin> <youtube token> <spotify token> <playlist 1 youtube ID> <playlist 1 spotify ID> [<playlist n youtube ID> <playlist n spotify ID>]\n" % sys.argv[0])
        print("where origin is the platform whose playlists should remain unchanged during the sync - either youtube or spotify (specify origin as both in order to merge the playlists from both platforms\n")