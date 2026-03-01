import requests
from django.http import JsonResponse    

def get_address_by_cep(request, cep):
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')

    if response.status_code == 200:
        data = response.json
        if 'erro' in data:
            return JsonResponse({'error': 'CEP não encontrado'}, status=404)
        return data
    else:
        return JsonResponse({'error': 'Erro ao consultar o CEP. Tente novamente mais tarde.'}, status=500)