from advance_model import AdvanceGameRunner, ReplayRunner
from displayer import TextGameDisplayer,GUIGameDisplayer
from utils import *
import sys
import os
import importlib
import traceback
import datetime
import time
import pickle
import random
import players.random_player as random_player
from optparse import OptionParser

idx2rb = ["teamRed","teamBlue"]

def loadAgent(file_list,name_list,superQuiet = True):
    players = [None] * 2
    load_errs = {}
    for i,player_file_path in enumerate(file_list):
        player_temp = None
        try:
            mymodule = importlib.import_module(player_file_path)
            # students need to name their player as follows
            player_temp = mymodule.myPlayer(i)
        except (NameError, ImportError):
            #print('Error: The team "' + player_file_path + '" could not be loaded! ', file=sys.stderr)
            #traceback.print_exc()
            pass

        except IOError:
            #print('Error: The team "' + player_file_path + '" could not be loaded! ', file=sys.stderr)
            #traceback.print_exc()
            pass
        except:
            pass

        # if student's player does not exists, using random player
        if player_temp != None:
            players[i] = player_temp
            if not superQuiet:
                print ('Player {} team {} agent {} loaded'.format(i,name_list[i],file_list[i]))
        else:
            players[i] = random_player.myPlayer(i)
            load_errs[idx2rb[i]] = '[Error] Player {} team {} agent {} cannot be loaded'.format(i,name_list[i],".".join((file_list[i]).split(".")[-2:]))
    return players, load_errs


class HidePrint:
    # setting output steam
    def __init__(self,flag,file_path,f_name):
        self.flag = flag
        self.file_path = file_path
        self.f_name = f_name
        self._original_stdout = sys.stdout

    def __enter__(self):
        if self.flag:
            if not os.path.exists(self.file_path):
                os.makedirs(self.file_path)
            sys.stdout = open(self.file_path+"/log-"+self.f_name+".log", 'w')
            sys.stderr = sys.stdout
        else:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = sys.stdout

    # Restore
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = sys.stdout


def run(options):

    # text displayer, will disable GUI
    displayer = GUIGameDisplayer(options.delay)
    if options.textgraphics:
        displayer = TextGameDisplayer()
    elif options.quiet or options.superQuiet:
        displayer = None

    players_names = [options.redName, options.blueName] 
    for i in range(2):
        players_names[i] = players_names[i].replace(" ","_")

    # if random seed is not provide, using timestamp
    if options.setRandomSeed == 90054:
        random_seed = int(str(time.time()).replace('.', ''))
    else:
        random_seed = options.setRandomSeed
    
    # make sure random seed is traceable
    random.seed(random_seed)
    seed_list = [random.randint(0,1e10) for _ in range(1000)]
    seed_idx = 0

    warnning_time = options.warningTimeLimit
    startRound_warning_time = options.startRoundWarningTimeLimit
    num_of_warning = options.numOfWarnings
    file_path = options.output

    if options.replay != None:
        if not options.superQuiet:
            print('Replaying recorded game %s.' % options.replay)
        replay_dir = options.replay
        replay_dir = os.path.join(options.output,replay_dir)
        if "." not in replay_dir:
            replay_dir +=".replay"
        if ".\\" in replay_dir:
            replay_dir.replace(".\\","")
        replay = pickle.load(open(replay_dir,'rb'),encoding="bytes")
        ReplayRunner(replay,displayer).Run()
    else: 
        games_results = [(0,0,0,0,0,0,0)]
        for i in range(options.multipleGames):
            # loading players
            players,load_errs = loadAgent([options.red,options.blue],players_names,superQuiet= options.superQuiet)
            is_load_err = False
            for i,err in load_errs.items():
                if not options.superQuiet:
                    print (i,err)
                is_load_err = True
        
            random_seed=seed_list[seed_idx]
            seed_idx += 1

            if is_load_err:
                results = {}
                results["options"] = options
                results["load_errs"] = load_errs
                return results                

            f_name = players_names[0]+'-vs-'+players_names[1]+"-"+datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S-%f")
            
            gr = AdvanceGameRunner(players,
                            seed=random_seed,
                            time_limit=warnning_time,
                            startRound_time_limit = startRound_warning_time,
                            warning_limit=num_of_warning,
                            displayer=displayer,
                            players_namelist=players_names)
            with HidePrint(options.saveLog,file_path,f_name):                
                replay = gr.Run()

            _,_,r_total,b_total,r_win,b_win,tie = games_results[len(games_results)-1]
            r_score = replay[0][0]
            b_score = replay[1][0]
            r_total = r_total+r_score
            b_total = b_total+b_score
            if r_score==b_score:
                tie =  tie + 1
            elif r_score<b_score:
                b_win = b_win + 1
            else:
                r_win = r_win + 1
            if not options.superQuiet:
                print("Result of game ({}/{}): Player {} earned {} points; Player {} earned {} points\n".format(i+1,options.multipleGames,players_names[0],r_score,players_names[1],b_score))
            games_results.append((r_score,b_score,r_total,b_total,r_win,b_win,tie))

            if options.saveGameRecord:
                # f_name = file_path+"/replay-"+players_names[0]+'-vs-'+players_names[1]+datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S-%f")+'.replay'
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                if not options.superQuiet:
                    print("Game ({}/{}) has been recorded!\n".format(i+1,options.multipleGames))
                record = pickle.dumps(replay)
                with open(file_path+"/replay-"+f_name+".replay",'wb') as f:
                    f.write(record)
        _,_,r_total,b_total,r_win,b_win,tie = games_results[len(games_results)-1]
        r_avg = r_total/options.multipleGames
        b_avg = b_total/options.multipleGames
        r_win_rate = r_win / options.multipleGames *100
        b_win_rate = b_win / options.multipleGames *100
        if not options.superQuiet:
            print(
                "Over {} games: \nPlayer {} earned {:+.2f} points in average and won {} games, winning rate {:.2f}%; \nPlayer {} earned {:+.2f} points in average and won {} games, winning rate {:.2f}%; \nAnd {} games tied.".format(options.multipleGames,
                players_names[0],r_avg,r_win,r_win_rate,players_names[1],b_avg,b_win,b_win_rate,tie))

        # return results as statistics
        results = {}
        results["r_avg"] = r_avg
        results["b_avg"] = b_avg
        results["r_win"] = r_win
        results["b_win"] = b_win
        results["r_win_rate"] = r_win_rate
        results["b_win_rate"] = b_win_rate
        results["r_name"] = players_names[0]
        results["b_name"] = players_names[1]
        results["fileName"] = f_name
        results["options"] = options
        results["load_errs"] = load_errs
        results["tie"] = tie

        return results


def loadParameter():

    """
    Processes the command used to run Azul from the command line.
    """
    usageStr = """
    USAGE:      python runner.py <options>
    EXAMPLES:   (1) python runner.py
                    - starts a game with two NaivePlayer
                (2) python runner.py -r naive_player -b myPlayer
                    - starts a fully automated game where the red team is a NaivePlayer and blue team is myPlayer
    """
    parser = OptionParser(usageStr)

    parser.add_option('-r', '--red', help='Red team player file (default: naive_player)', default='naive_player')
    parser.add_option('-b', '--blue', help='Blue team player file (default: naive_player)', default='naive_player')
    parser.add_option('--redName', help='Red team name (default: Red NaivePlayer)', default='Red NaivePlayer')
    parser.add_option('--blueName', help='Blue team name (default: Blue NaivePlayer)',default='Blue NaivePlayer')
    parser.add_option('-t','--textgraphics', action='store_true', help='Display output as text only (default: False)', default=False)
    parser.add_option('-q','--quiet', action='store_true', help='No text nor graphics output, only show game info', default=False)
    parser.add_option('-Q', '--superQuiet', action='store_true', help='No output at all', default=False)
    parser.add_option('-w', '--warningTimeLimit', type='float',help='Time limit for a warning of one move in seconds (default: 1)', default=1.0)
    parser.add_option('--startRoundWarningTimeLimit', type='float',help='Time limit for a warning of initialization for each round in seconds (default: 5)', default=5.0)
    parser.add_option('-n', '--numOfWarnings', type='int',help='Num of warnings a team can get before fail (default: 3)', default=3)
    parser.add_option('-m', '--multipleGames', type='int',help='Run multiple games in a roll', default=1)
    parser.add_option('--setRandomSeed', type='int',help='Set the random seed, otherwise it will be completely random (default: 90054)', default=90054)
    parser.add_option('-s','--saveGameRecord', action='store_true', help='Writes game histories to a file (named by teams\' names and the time they were played) (default: False)', default=False)
    parser.add_option('-o','--output', help='output directory for replay and log (default: output)',default='output')
    parser.add_option('-l','--saveLog', action='store_true',help='Writes player printed information into a log file(named by the time they were played)', default=False)
    parser.add_option('--replay', default=None, help='Replays a recorded game file by a relative path')
    parser.add_option('--delay', type='float', help='Delay action in a play or replay by input (float) seconds (default 0.1)', default=0.1)

    options, otherjunk = parser.parse_args(sys.argv[1:] )
    assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)

    #quick fixed on the naming, might need to be changed when the contest environment is fixed
    options.red = "players."+options.red
    options.blue = "players."+options.blue

    return options


if __name__ == '__main__':

    """
    The main function called when advance_model.py is run
    from the command line:

    > python runner.py

    See the usage string for more details.

    > python runner.py --help
    """

    options = loadParameter()
    run(options)





