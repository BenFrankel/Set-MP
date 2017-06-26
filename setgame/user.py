import os.path
import pickle
import time
import socket

from setgame.style import default


def get_local_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    result = s.getsockname()[0]
    s.close()

    return result


def gen_id():
    return 1  # TODO


def save_user_data(filename, model):
    with open(filename, 'w') as f:
        pickle.dump(model, f)


def load_user_model(filename):
    with open(filename, 'r') as f:
        return pickle.load(f)


def create_user(dir_user_data, name):
    new_model = UserModel(name, gen_id(),
                          None, [], [],
                          [],
                          time.time(),
                          None,
                          None,
                          None,
                          [], [], [], [])

    new_model.change_address(local_address)  # TODO: Get local IP address
    new_model.save(dir_user_data)

    return User(new_model)


def login(dir_user_data, id_):
    model = load_user_model(os.path.join(dir_user_data, id_))
    user = User(model)
    if local_address != model.address:
        model.change_address(local_address)
        model.save()
    user.broadcast()
    return user


class AddressInfo:
    def __init__(self, address, num_logins, first_login, last_login):
        self.address = address
        self.num_logins = num_logins
        self.first_login = first_login
        self.last_login = last_login

    @property
    def recurrence(self):
        time_span = self.last_login - self.first_login
        return time_span / 43200000 + self.num_logins


class PublicData:
    def __init__(self, user):
        self.name = user.label_name
        self.id = user.id
        self.address = user.address
        self.common_addresses = user.common_addresses()
        self.friends = user.friends
        self.version = user.version


class UserModel:
    def __init__(self, name, id_, address, address_info, common_addresses, style, options, controls, friends,
                 outgoing_requests, sent_requests, received_requests, history, version):
        # Identification
        self.name = name
        self.id = id_

        # Address
        self.address = address
        self.address_info = address_info
        self.common_addresses = common_addresses

        # Configuration
        self.style = style
        self.options = options
        self.controls = controls

        # Friend list
        self.friends = friends
        self.outgoing_requests = outgoing_requests
        self.sent_requests = sent_requests
        self.received_requests = received_requests

        # History
        self.history = history

        # Version
        self.version = version

    def change_address(self, address):
        self.address = address
        current_time = time.time()
        if address not in self.address_info:
            address_info = AddressInfo(address, 1, current_time, current_time)
            self.address_info[address] = address_info
        else:
            address_info = self.address_info[address]
        address_info.num_logins += 1
        address_info.last_login = current_time
        if address_info.recurrence > 10:
            self.common_addresses.append(address)
            self.common_addresses.sort(lambda x: x.recurrence)

    def save(self, dir_user_data):
        self.version += 1
        save_user_data(dir_user_data, self)


class User:
    def __init__(self, model):
        self.model = model
        self.online = True
        self.connections = []

    def broadcast(self):
        public_data = PublicData(self.model)
        for friend in self.model.friends:
            # TODO: Send public data to friend
            pass

    def notify_all(self):
        public_data = PublicData(self.model)
        for friend in self.connections:
            # TODO: Send public data to friend
            pass

    def rename(self, name):
        self.model.label_name = name
        self.model.save()
        self.notify_all()
