NEW2OLD = {'AD': 'ADCY8', 'DP': 'DPYS', 'GA': 'GARL1', 'HA9': 'HOXA9',
           'GR': 'GRM6', 'H12': 'HOXD12', 'HD9': 'HOXD9', 'PR': 'PRAC',
           'PT': 'PTGDR', 'SA': 'SALL3', 'SI': 'SIX6', 'SL': 'SLC6A2',
           'TL': 'TLX3', 'TR': 'TRIM58', 'ZF': 'ZFP41'}
OLD2NEW = {NEW2OLD[i]: i for i in NEW2OLD.keys() if NEW2OLD[i] is not None}

def short_2_full(short):
    return NEW2OLD[short.strip().upper()]

def full_2_short(full):
    return OLD2NEW[full.strip().upper()]
