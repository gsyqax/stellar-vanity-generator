from stellar_base import keypair as k
from stellar_base.keypair import Keypair
from stellar_base.operation import CreateAccount, Payment
from stellar_base.transaction import Transaction
from stellar_base.transaction_envelope import TransactionEnvelope as Te
from stellar_base.memo import TextMemo
from stellar_base.horizon import horizon_livenet
from time import time, sleep
from multiprocessing import Process, Pipe

# This creates a new Horizon Livenet instance
SUFFIX_TO_SEARCH = "XLM"
PREFIX_TO_SEARCH = None
PROCESS_COUNT = 12
horizon = horizon_livenet()

SAMPLE_DICT = ['ABLE', 'ABOUT', 'ABOVE', 'AFTER', 'AGAIN', 'ALSO', 'ALWAYS', 'AMONG', 'ANIMAL', 'ANSWER', 'APPEAR', 'AREA', 'BACK', 'BASE', 'BEAUTY', 'BEEN', 'BEFORE', 'BEGAN', 'BEGIN', 'BEHIND', 'BEST', 'BETTER', 'BIRD', 'BLACK', 'BLUE', 'BOAT', 'BODY', 'BOOK', 'BOTH', 'BRING', 'BUILD', 'BUSY', 'CALL', 'CAME', 'CARE', 'CARRY', 'CAUSE', 'CENTER', 'CHANGE', 'CHECK', 'CITY', 'CLASS', 'CLEAR', 'CLOSE', 'COLD', 'COLOR', 'COME', 'COMMON', 'COULD', 'COURSE', 'COVER', 'CROSS', 'DARK', 'DECIDE', 'DEEP', 'DIFFER', 'DIRECT', 'DOES', "DON'T", 'DONE', 'DOOR', 'DOWN', 'DRAW', 'DRIVE', 'DURING', 'EACH', 'EARLY', 'EARTH', 'EASE', 'EAST', 'ENOUGH', 'EVEN', 'EVER', 'EVERY', 'FACE', 'FACT', 'FALL', 'FAMILY', 'FARM', 'FAST', 'FATHER', 'FEEL', 'FEET', 'FIELD', 'FIGURE', 'FILL', 'FINAL', 'FIND', 'FINE', 'FIRE', 'FIRST', 'FISH', 'FIVE', 'FOLLOW', 'FOOD', 'FOOT', 'FORCE', 'FORM', 'FOUND', 'FOUR', 'FREE', 'FRIEND', 'FROM', 'FRONT', 'FULL', 'GAVE', 'GIRL', 'GIVE', 'GOLD', 'GOOD', 'GOVERN', 'GREAT', 'GREEN', 'GROUND', 'GROUP', 'GROW', 'HALF', 'HAND', 'HAPPEN', 'HARD', 'HAVE', 'HEAD', 'HEAR', 'HEARD', 'HEAT', 'HELP', 'HERE', 'HIGH', 'HOLD', 'HOME', 'HORSE', 'HOUR', 'HOUSE', 'IDEA', 'INCH', 'ISLAND', 'JUST', 'KEEP', 'KIND', 'KING', 'KNEW', 'KNOW', 'LAND', 'LARGE', 'LAST', 'LATE', 'LAUGH', 'LEAD', 'LEARN', 'LEAVE', 'LEFT', 'LESS', 'LETTER', 'LIFE', 'LIGHT', 'LIKE', 'LINE', 'LIST', 'LISTEN', 'LITTLE', 'LIVE', 'LONG', 'LOOK', 'LOVE', 'MADE', 'MAIN', 'MAKE', 'MANY', 'MARK', 'MEAN', 'MIGHT', 'MILE', 'MIND', 'MINUTE', 'MISS', 'MONEY', 'MOON', 'MORE', 'MOST', 'MOTHER', 'MOVE', 'MUCH', 'MUSIC', 'MUST', 'NAME', 'NEAR', 'NEED', 'NEVER', 'NEXT', 'NIGHT', 'NORTH', 'NOTE', 'NOTICE', 'NOUN', 'NUMBER', 'OBJECT', 'OFTEN', 'ONCE', 'ONLY', 'OPEN', 'ORDER', 'OTHER', 'OVER', 'PAGE', 'PAPER', 'PART', 'PASS', 'PEOPLE', 'PERSON', 'PIECE', 'PLACE', 'PLAIN', 'PLAN', 'PLANE', 'PLANT', 'PLAY', 'POINT', 'PORT', 'POSE', 'POUND', 'POWER', 'PRESS', 'PULL', 'QUICK', 'RAIN', 'REACH', 'READ', 'READY', 'REAL', 'RECORD', 'REST', 'RIGHT', 'RIVER', 'ROAD', 'ROCK', 'ROOM', 'ROUND', 'RULE', 'SAID', 'SAME', 'SCHOOL', 'SECOND', 'SEEM', 'SELF', 'SERVE', 'SHAPE', 'SHIP', 'SHORT', 'SHOULD', 'SHOW', 'SIDE', 'SIMPLE', 'SINCE', 'SING', 'SIZE', 'SLEEP', 'SLOW', 'SMALL', 'SNOW', 'SOME', 'SONG', 'SOON', 'SOUND', 'SOUTH', 'SPELL', 'STAND', 'STAR', 'START', 'STATE', 'STAY', 'STEP', 'STILL', 'STOOD', 'STOP', 'STORY', 'STREET', 'STRONG', 'STUDY', 'SUCH', 'SURE', 'TABLE', 'TAIL', 'TAKE', 'TALK', 'TEACH', 'TELL', 'TEST', 'THAN', 'THAT', 'THEIR', 'THEM', 'THEN', 'THERE', 'THESE', 'THEY', 'THING', 'THINK', 'THIS', 'THOSE', 'THOUGH', 'THREE', 'TIME', 'TOLD', 'TOOK', 'TOWARD', 'TOWN', 'TRAVEL', 'TREE', 'TRUE .', 'TURN', 'UNDER', 'UNIT', 'UNTIL', 'USUAL', 'VERY', 'VOICE', 'VOWEL', 'WAIT', 'WALK', 'WANT', 'WARM', 'WATCH', 'WATER', 'WEEK', 'WEIGHT', 'WELL', 'WENT', 'WERE', 'WEST', 'WHAT', 'WHEEL', 'WHEN', 'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE', 'WILL', 'WIND', 'WITH', 'WONDER', 'WOOD', 'WORD', 'WORK', 'WORLD', 'WOULD', 'WRITE', 'YEAR', 'YOUNG', 'YOUR']

def new_addr():
    a = k.Keypair.random()
    return a.address().decode('utf-8'), a

def get_addr_mp(pipe, suffix=None, prefix=None, process_id=0):
    #time_prev = time()
    #time_next = time()
    last_kps = 0
    prefix_len = len(prefix) if prefix != None else None
    suffix_len = len(suffix) if suffix != None else None
    count = 0
    delta_count = 0
    while True:
        if pipe.poll():
            msg = pipe.recv()
            if msg == 'kill':
                pipe.send("killed;%d" % process_id)
                return False
        delta_count = 0
        addr, a = new_addr()
        if (prefix == None or addr.startswith(prefix)) and (suffix == None or addr.endswith(suffix)):
            pipe.send("result;" + a.seed().decode() + "," + a.address().decode())
            #print("\nProcess", process_id, "killed.")   
            pipe.send("killed;%d" % process_id)
            return True
        count+=1
        pipe.send("kcount;" + str(count))


def export_keypair(seed, address, filename):
    f = open(filename, "w")
    f.write("private,public\n")
    f.write(seed + "," + address)
    f.close()

def spawn_processes(target, prefix, suffix, count=1):
    parent_pipes = []
    child_pipes = []
    processes = []
    for i in range(count):
        pp, cc = Pipe()
        proc = Process(target=target, args=(cc,), kwargs={"suffix": suffix, "prefix":prefix, "process_id":i})
        parent_pipes.append(pp)
        child_pipes.append(cc)
        processes.append(proc)
        proc.start()
    return processes, parent_pipes, child_pipes


if __name__ == '__main__':
    time_prev = time()
    time_next = time()
    time_last_print = time()
    suffix = input("Suffix to search [enter for none]: ")
    prefix = input("Prefix to search [enter for none]: ")
    process_count = PROCESS_COUNT
    result = None
    keys_analyzed_count = 0
    delta_keys_count = 0
    process_key_counts = [0 for x in range(process_count)]
    old_counts = [0 for i in range(process_count)]
    new_counts = [0 for i in range(process_count)]
    processes, parent_pipes, child_pipes = spawn_processes(get_addr_mp, prefix, suffix, count=process_count)
    while True:
        delta_keys_count = 0
        for i in range(len(parent_pipes)):
            while parent_pipes[i].poll():
                msg = parent_pipes[i].recv()
                if msg.startswith("result"):
                    result = msg.split(";")[1]
                    for pp in parent_pipes:
                        pp.send("kill")
                    print()
                    #should_break=True
                elif msg.startswith("kcount"):
                    new_count = int(msg.split(";")[1])
                    new_counts[i] = new_count
                elif msg.startswith("killed"):
                    process_id = msg.split(";")[1]
                    print("Process %s killed" % process_id)
        if not any(process.is_alive() for process in processes):
            break
        time_next = time()
        if time_next - time_last_print >= 0.5 and result == None:
            delta_ct = 0
            for i in range(len(new_counts)):
                delta_ct += (new_counts[i] - old_counts[i])
                old_counts[i] = new_counts[i]
            last_kps = int(delta_ct / (time_next - time_last_print))
            print("Analized:", sum(new_counts), "keys;", last_kps, "kps", end="\r")
            time_last_print = time()
        time_prev = time()
        sleep(0.1)
            
    seed, address = result.split(",")
    print("Seed:", seed, "Address:", address)
    wants_save_file = input("Save to file? [Y/n] " )
    if wants_save_file.lower() == 'y':
        filename = input("Enter filename (CSV): ")
        if not filename.endswith(".csv"):
            filename = filename + ".csv"
        export_keypair(seed, address, filename) 
