def check_user_and_request(request):
    if request is None or request.user.is_anonymous:
        return False, None
    return True, request.user
