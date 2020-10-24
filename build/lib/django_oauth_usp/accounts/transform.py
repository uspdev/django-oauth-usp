class Mapper:
    def get_mapper(self):
        return {
            'loginUsuario': 'login',
            'nomeUsuario': 'name',
            'tipoUsuario': 'user_type',
            'emailPrincipalUsuario': 'main_email',
            'emailAlternativoUsuario': 'alternative_email',
            'emailUspUsuario': 'usp_email',
            'numeroTelefoneFormatado': 'formatted_phone',
            'wsuserid': 'wsuserid',
            'vinculo': 'bind'
        }


class Transform:
    mapper = Mapper

    def transform_data(self, data):
        mapper = self.mapper().get_mapper()
        transformed = dict()
        for key in mapper:
            if key in data:
                transformed.update({mapper.get(key): str(data.get(key))})

        return transformed
