
def supervisor(state):
    if not state["research"]:
        return {"next": "researcher"}
    elif not state['article']:
        return {"next":"writer"}
    elif not state['review']:
        return {"next":"reviewer"}
    else:
        return {
            "next":"FINISH"
        }