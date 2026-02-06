MET={"total":0,"allowed":0,"blocked":0,"abstained":0}

def update_metrics(t):
    MET["total"]+=1
    if t=="ALLOWED": MET["allowed"]+=1
    if t=="BLOCKED": MET["blocked"]+=1
    if t=="ABSTAINED": MET["abstained"]+=1

def get_metrics():
    return MET
