

from .categorize import connect_to_commons
from .owid_config import load_credentials
from .api_services import get_category_members_titles

username, password = load_credentials()

if username and password:

    site = connect_to_commons(username, password)

    members = get_category_members_titles(
        site,
        "Category:Uploaded_by_OWID_importer_tool",
        namespace=6,
    )
