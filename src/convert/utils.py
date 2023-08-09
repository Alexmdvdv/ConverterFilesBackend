from src.convert.models import ApiKey


def get_next_api_key():
    try:
        api_key = ApiKey.objects.filter(requests_remaining__gt=0).order_by('id').first()
        if api_key:
            return api_key.key

        else:
            return None

    except ApiKey.DoesNotExist:
        return None


