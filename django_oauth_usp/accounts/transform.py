import json


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
                transformed.update({mapper.get(key): self.to_text(data.get(key))})

        return transformed

    def to_text(self, value):
        """None vira texto vazio; listas e dicts (como o vínculo) são gravados em JSON."""
        if value is None:
            return ''
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
