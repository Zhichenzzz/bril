import json
import sys
from collections import OrderedDict

TEMINATORS = {"jmp", "br", "ret"} # call is not a terminator

def form_blocks(body):
    blocks = []
    cur_block = []
    for instr in body:
        if 'op' in instr: # An actual instruction, normal or terminator
            cur_block.append(instr)
            if instr['op'] in TEMINATORS:
                yield cur_block
                cur_block = []
        else: # A label
            if cur_block:
                yield cur_block
            cur_block = [instr]
    if cur_block:
        yield cur_block

def block_map(blocks):
    out = OrderedDict()
    for block in blocks:
        if 'label' in block[0]:
            name = block[0]['label']
            block = block[1:]
        else:
            name = 'b{}'.format(len(out))
        out[name] = block
    return out
 
def get_cfg(name2block):
    """Given a name2block map, produce a mapping from block names to successors block names"""
    out = {}
    for i, (name, block) in enumerate(name2block.items()):
        
        last = block[-1]
        if last['op'] in {'jmp', 'br'}:
            succ_name = last['labels']
        elif last['op'] == 'ret':
            succ_name = []
        else:
            if i < len(name2block) - 1:
                succ_name = [list(name2block.keys())[i+1]]
            else:
                succ_name = []

        out[name] = succ_name
    return out

def mycfg():
    prog = json.load(sys.stdin)
    for function in prog["functions"]:
        name2blcok = block_map(form_blocks(function["instrs"]))
        # for name, block in name2blcok.items():
        #     print(name)
        #     print("  ", block)
        cfg = get_cfg(name2blcok)
        print('digraph {} {{'.format(function['name']))
        for name in name2blcok:
            print('  {};'.format(name))
        for name, succs in cfg.items():
            print('  {} -> {{{}}}'.format(name, ', '.join(succs)))
        print('}')
if __name__ == '__main__':
    mycfg()

# bril2json <  ../test/interp/core/br.bril | python mycfg.py | dot -Tpdf -o cfg.pdf
# turnt --diff jmp.bril 
# turnt -vp jmp.bril