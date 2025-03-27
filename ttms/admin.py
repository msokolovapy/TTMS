from ttms.models_user import login_checks_pass
from ttms.general_use_functions import obtain_info_from_session, convert_to_boolean, \
                                       build_web_page, redirect_to_web_page
def login_check_and_redirect(check_availability_matches):
    if login_checks_pass():
          admin_name,matches = obtain_info_from_session()
          check_availability_matches = convert_to_boolean(check_availability_matches)
          return build_web_page('admin', admin_name, matches.to_display(), check_availability_matches)
    return redirect_to_web_page('login')





