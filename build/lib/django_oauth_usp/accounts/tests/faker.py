from faker import Faker
from faker.providers import BaseProvider, internet


fake = Faker('pt_BR')

data = {
    'login': fake.user_name(),
    'name': fake.name(),
    'user_type': fake.random_elements(elements=('I', 'E'))[0],
    'main_email': fake.email(),
    'alternative_email': fake.email(),
    'usp_email': fake.email(),
    'formatted_phone': fake.phone_number(),
    'wsuserid': fake.msisdn(),
    'bind': '[]',
}


class Resource(BaseProvider):
    def resource(self):
        return {
            'loginUsuario': data.get('login'),
            'nomeUsuario': data.get('name'),
            'tipoUsuario': data.get('user_type'),
            'emailPrincipalUsuario': data.get('main_email'),
            'emailAlternativoUsuario': data.get('alternative_email'),
            'emailUspUsuario': data.get('usp_email'),
            'numeroTelefoneFormatado': data.get('formatted_phone'),
            'wsuserid': data.get('wsuserid'),
            'vinculo': data.get('bind')
        }

    def resource_transformed(self):
        return data


fake.add_provider(Resource)
