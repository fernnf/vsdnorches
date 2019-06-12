from SliceManager import VirtualSwitch


if __name__ == '__main__':
    v = VirtualSwitch("23", "name","edef")

    print(v.serialize())