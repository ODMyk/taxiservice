import os, sys, json

path = sys.argv[0]
if not os.path.isdir(path):
    path = "\\".join((path, ".."))

def get_data(name: str) -> list:
    with open(f"{path}\\{name}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    return list(data)

def save(type_, obj: dict) -> None:
    objs = get_data(type_)
    objs.append(obj)

    with open(f"{path}\\{type_}.json", "w+", encoding="utf-8") as file:
        json.dump(objs, file)

def send_error(sock, addres):
    sock.sendto("ERROR".encode("utf-8"), addres)

def parse_add(data) -> tuple:
    type_ = data['type']

    if type_ == "car":
        msg = "Ваше авто успешно зарегистрировано в системе"
        obj = {
            "mark": data['mark'],
            "model": data['model']
        }
    elif type_ == "order":
        msg = "Ваш заказ успешно зарегистрирован в системе"
        obj = {
            "mark": data["mark"],
            'model': data['model'],
            "phone": data["phone"]
        }
    
    return (obj, msg.encode("utf-8"))

def parse_request(sock, addres, data):
    if data.startswith("/get"):
        args = data.split(" ")[1:]
        
        if args[0] in ("cars", "orders"):
            data_to_return = get_data(args[0])
            msg = json.dumps(data_to_return).encode("utf-8")
            sock.sendto(msg, addres)
        else:
            send_error(sock, addres)
    elif data.startswith("/add"):
        args = json.loads(data.lstrip('/add '))
        
        if args['type'] in ("order", "car"):
            obj, msg = parse_add(args)
            save("".join((args['type'], "s")), obj)
            sock.sendto(msg, addres)
    else:
        send_error(sock, addres)

