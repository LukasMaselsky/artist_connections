from artist_connections.extras.friends import main as friends
from artist_connections.extras.network import main as network
from artist_connections.extras.connections import main as connections
from artist_connections.extras.collaborators import main as collaborators
from artist_connections.extras.cycles import main as cycles
from artist_connections.extras.common import main as common
from artist_connections.extras.separation import main as separation
from artist_connections.extras.features import main as features
from artist_connections.helpers.helpers import int_input, print_options

#* run with 'python -m artist_connections'

def main():

    options = {
        "Network": network, 
        "Connections": connections, 
        "Collaborators": collaborators, 
        "Separation": separation, 
        "Cycles": cycles, 
        "Common": common,
        "Features": features,
        "Friends": friends
    }

    options_list = list(options.keys())
    print_options(options_list)

    choose = int_input("Choose what to do with the data: ", len(options) - 1)
    options[options_list[choose]]()
    

    return

    
    
if __name__ == "__main__":
    main()