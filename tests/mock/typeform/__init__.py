# typeform Provider
from faker import Faker
# first, import a similar Provider or use the default one
from faker.providers import BaseProvider

# create new provider class
class Provider(BaseProvider):

    state_choices = ["CA - California",
                     "AL - Alabama",
                     "AZ - Arizona",
                     "CA - California",
                     "CT - Connecticut",
                     "FL - Florida",
                     "HI - Hawaii",
                     "IL - Illinois",
                     "IA - Iowa",
                     "KY - Kentucky",
                     "ME - Maine",
                     "MA - Massachusetts",
                     "MN - Minnesota",
                     "MO - Missouri",
                     "NE - Nebraska",
                     "NH - New Hampshire",
                     "NM - New Mexico",
                     "NC - North Carolina",
                     "OH - Ohio",
                     "OR - Oregon",
                     "RI - Rhode Island",
                     "SD - South DakotaND",
                     "TX - Texas",
                     "VT - Vermont",
                     "WA - Washington",
                     "WI - Wisconsin"]

    phone_type_choices = [
        "Cell phone",
        "Work phone",
        "Home phone",
        "Other",
    ]

    @classmethod
    def state_choice(cls):
        chances = []
        for n in cls.state_choices:
            if 'CA' in n:
                chances.append(0.45)
            else:
                chances.append(0.1/48.0)
        return cls.random_element(dict(zip(cls.state_choices, chances)))


    def set_phone(self, answers):
        has_phone = self.random_element({1: .8, 0: 0.2})
        answers['yesno_15075861'] = "1" if has_phone else "0"
        if has_phone:
            answers['textfield_15076839'] = self.generator.phone_number()
            phone_type = self.random_element(self.phone_type_choices)
            answers['list_15076883_choice'] = phone_type
            if phone_type == self.phone_type_choices[-1]:
                 answers['list_15076883_other'] = self.generator.word()
        return answers

    def outside_convictions(self, answers):
        was_convicted_elsewhere = self.random_element({1: .25, 0: 0.75})
        answers['yesno_15076784'] = "1" if was_convicted_elsewhere else "0"
        if was_convicted_elsewhere:
            answers['textarea_15076790'] = '\n'.join(self.generator.sentences(3))
        return answers

    def probation(self, answers):
        on_probation = self.random_element({1: .1, 0: 0.9})
        answers['yesno_15076722'] = "1" if on_probation else "0"
        if on_probation:
            answers['textfield_15076739'] = ", ".join([self.generator.city(), self.generator.state_abbr()])
            answers['textfield_15076767'] = self.generator.date_time_between('now','+5y').strftime('%b %Y')
        return answers

    def set_address(self, answers):
        has_address = self.random_element({1: .9, 0: 0.1})
        answers['yesno_15075591'] = "1" if has_address else "0"
        if has_address:
            answers.update({
                "textfield_15075763": self.generator.street_address(),
                "textfield_15075797": self.generator.city(),
                "textfield_15075851": self.generator.zipcode(),
                "dropdown_15075846": self.state_choice(),
            })
        return answers

    def answers(self):
        answers = {
            "date_15075567": self.generator.date_time_between('-70y','-18y').strftime('%Y-%m-%d'),
            "email_15077308": self.generator.free_email(),
            "textfield_15075498": self.generator.first_name(),
            "textfield_15075501": self.generator.last_name(),
            "textfield_15075504": self.random_element([self.generator.first_name(), self.generator.last_name()]),
            "textfield_15075537": self.random_element([self.generator.ssn(),""]),
            "textfield_15075547": self.random_element([self.bothify('#???????'),""]),
            "textfield_15076804": self.random_int(max=4000),
            "textfield_15076814": self.random_int(max=2000),
            "textfield_15076818": self.random_element([" ".join(self.generator.words(5)),""]),
            "yesno_15075576": self.random_element({"1": 0.8, "0": 0.2}),
            "yesno_15076724": self.random_element({"1": 0.1, "0": 0.9}),
            "yesno_15076728": self.random_element({"1": 0.1, "0": 0.9}),
            "yesno_15076795": self.random_element({"1": 0.6, "0": 0.4}),
            }
        answers = self.set_phone(answers)
        answers = self.set_address(answers)
        answers = self.outside_convictions(answers)
        answers = self.probation(answers)
        return answers
