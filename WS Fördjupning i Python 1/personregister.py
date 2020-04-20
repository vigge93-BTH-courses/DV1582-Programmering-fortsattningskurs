import json


class AreaCode:
    def __init__(self, code, townname):
        self.code = code
        self.townname = townname

    def __str__(self):
        return "{} {} {}".format(
            self.code // 100,
            self.code % 100,
            self.townname)

    def to_dict(self):
        return {
            'code': self.code,
            'townname': self.townname
        }

    @staticmethod
    def refactor(data):
        return AreaCode(data['code'], data['townname'])


class Address:
    def __init__(self, streetname, number, areacode):
        self.streetname = streetname
        self.number = number
        self.areacode = areacode

    def __str__(self):
        return "{} {}\n{}".format(
            self.streetname,
            self.number,
            self.areacode)

    def to_dict(self):
        return {
            'streetname': self.streetname,
            'number': self.number,
            'areacode': self.areacode.to_dict()
        }

    @staticmethod
    def refactor(data):
        areacode = AreaCode.refactor(data['areacode'])
        return Address(data['streetname'], data['number'], areacode)


class Person:
    def __init__(self, name, year, address):
        self.name = name
        self.birthyear = year
        self.address = address

    def __str__(self):
        return "{},{}\n{}".format(
            self.name,
            self.birthyear,
            self.address)

    def to_dict(self):
        return {
            'name': self.name,
            'birthyear': self.birthyear,
            'address': self.address.to_dict()
        }

    @staticmethod
    def refactor(data):
        address = Address.refactor(data['address'])
        return Person(data['name'], data['birthyear'], address)


class Register:
    def __init__(self):
        self.record = []

    def __str__(self):
        outstr = ""
        for rec in self.record:
            outstr += str(rec)
            outstr += "\n\n"

        return outstr

    def addPerson(self, file):
        self.record.append(file)

    def to_dict(self):
        return {
            'record': [person.to_dict() for person in self.record]
        }

    @staticmethod
    def refactor(data):
        register = Register()
        for record in data['record']:
            person = Person.refactor(record)
            register.addPerson(person)
        return register


if __name__ == "__main__":
    rec = Register()
    rec.addPerson(Person("Torfrej Persdotter", 1980, Address(
        "Almgatan.", 10, AreaCode(37287, "Hogsala"))))
    rec.addPerson(Person("Bohenrika Svensson", 1948, Address(
        "Fiskgatan.", 31, AreaCode(28192, "Botorp"))))
    rec.addPerson(Person("Halvdan Lenbakt", 1999, Address(
        "Storskogen", 61, AreaCode(97212, "Fjosiken"))))

    print(rec)

    data = rec.to_dict()
    jsondata = json.dumps(data)
    print(jsondata)

    data_read = json.loads(jsondata)
    rec_read = Register.refactor(data_read)
    print(rec_read)
