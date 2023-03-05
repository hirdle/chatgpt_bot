import pysondb
db = pysondb.getDb("dialogs.json")


def getLenDialogsUsers():
    return len(db.getAll())

def getDialog(id):
    dialog = db.getByQuery({"userid": id})
    if dialog == []:
        createDialog(id)
        dialog = db.getByQuery({"userid": id})
    return dialog[0]

def createDialog(id):
    db.add({"userid": id, "messages": []})
    return getDialog(id)

def addDialog(id, q, a):

    dialog = getDialog(id)

    if dialog == []:
        dialog = createDialog(id)

    dialog['messages'].append({"role": "user", "content": q})
    dialog['messages'].append({"role": "assistant", "content": a})

    db.updateByQuery({"userid": id}, {"messages": dialog['messages']})
    return dialog

def clearDialog(id):
    db.updateByQuery({"userid": id}, {"messages": []})