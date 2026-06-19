from .main_app.api_services import get_category_members_titles
from .main_app.categorize import connect_to_commons
from .main_app.owid_config import load_credentials

username, password = load_credentials()

if username and password:

    site = connect_to_commons(username, password)

    members = get_category_members_titles(
        site,  # type: ignore
        "Category:Uploaded_by_OWID_importer_tool",
        namespace=6,
    )
