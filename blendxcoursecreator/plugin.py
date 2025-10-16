import os
from glob import glob

import click
import importlib_resources

from tutor import hooks
from tutormfe.hooks import MFE_APPS

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'BLENDXCOURSECREATOR_'.
        ("BLENDXCOURSECREATOR_VERSION", __version__),
        ("BLENDXCOURSECREATOR_ENTERPRISE_PLAN", False),

        # OpenAI API Key
        ("BLENDXCOURSECREATOR_OPENAI_API_KEY", "sk-your-api-key-here"),

        # Portkey Configuration
        ("BLENDXCOURSECREATOR_ENABLE_PORTKEY", False),
        ("BLENDXCOURSECREATOR_PORTKEY_API_KEY", "your-api-key-here"),
        ("BLENDXCOURSECREATOR_PORTKEY_EMBEDDING_MODEL", "text-embedding-3-large"),
        ("BLENDXCOURSECREATOR_PORTKEY_IMAGE_MODEL", "dall-e-3"),
        ("BLENDXCOURSECREATOR_PORTKEY_CHAT_MODEL", "gpt-4.1"),
        ("BLENDXCOURSECREATOR_PORTKEY_CHAT_PROVIDER", "@blended-chat"),
        ("BLENDXCOURSECREATOR_PORTKEY_IMAGE_PROVIDER", "@blended-image"),
        ("BLENDXCOURSECREATOR_PORTKEY_EMBEDDING_PROVIDER", "@blended-embedding"),

        # Blend-ed Cloud AI Course Creator API Key
        ("BLENDXCOURSECREATOR_BLENDX_AICC_KEY", "your-api-key-here"),
        ("BLENDXCOURSECREATOR_BLENDX_AICC_APP_URL", "https://aicc.blendxed.com"),
        ("BLENDXCOURSECREATOR_BLENDX_AICC_API_TYPE", "blendxcoursecreator"),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("blendxcoursecreator") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``blendxcoursecreator/templates/blendxcoursecreator/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/blendxcoursecreator/build``.
    [
        ("blendxcoursecreator/build", "plugins"),
        ("blendxcoursecreator/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in blendxcoursecreator/patches,
# apply a patch based on the file's name and contents.
for path in glob(str(importlib_resources.files("blendxcoursecreator") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


#######################################
# CUSTOM MFE APPS
#######################################

def _get_mfe_version():
    return os.getenv("COURSE_CREATOR_MFE_VERSION", "master")


@MFE_APPS.add()
def _add_my_mfe(mfes):

    mfes["course-creator"] = {
        "repository": "https://github.com/blend-ed/frontend-app-course-creator.git",
        "port": 8009,
        "version": _get_mfe_version()
    }
 
    return mfes