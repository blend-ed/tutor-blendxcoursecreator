import os
from glob import glob

import click
import importlib_resources
from dotenv import load_dotenv

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

        # BlendxCCApp Configuration
        ("BLENDXCCAPP_VERSION", __version__),
        ("BLENDXCCAPP_DOCKER_IMAGE", "{{ DOCKER_REGISTRY }}openedx/blendxccapp:{{ BLENDXCCAPP_VERSION }}"),
        ("BLENDXCCAPP_HOST", "aicc.{{ LMS_HOST }}"),
        ("BLENDXCCAPP_REPOSITORY", "https://github.com/blend-ed/blendxccapp.git"),
        ("BLENDXCCAPP_REPOSITORY_VERSION", "main"),
        ("BLENDXCCAPP_MYSQL_DATABASE", "blendxccapp"),
        ("BLENDXCCAPP_MYSQL_USERNAME", "blendxccapp"),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("BLENDXCCAPP_MYSQL_PASSWORD", "{{ 20|random_string }}"),
        ("BLENDXCCAPP_ADMIN_SECRET_KEY", "{{ 24|random_string }}"),
        ("BLENDXCCAPP_SECRET_KEY", "{{ 24|random_string }}"),
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


########################################
# DOCKER IMAGE MANAGEMENT
########################################

# Images to be built by `tutor images build`.
hooks.Filters.IMAGES_BUILD.add_items(
    [
        (
            "blendxccapp",
            ("plugins", "blendxcoursecreator", "build", "blendxccapp"),
            "{{BLENDXCCAPP_DOCKER_IMAGE}}",
            (),
        )
    ]
)

# Images to be pulled as part of `tutor images pull`.
hooks.Filters.IMAGES_PULL.add_items(
    [
        (
            "blendxccapp",
            "{{ BLENDXCCAPP_DOCKER_IMAGE }}"
        )
    ]
)

# Images to be pushed as part of `tutor images push`.
hooks.Filters.IMAGES_PUSH.add_items(
    [
        (
            "blendxccapp",
            "{{ BLENDXCCAPP_DOCKER_IMAGE }}"
        )
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# MySQL init task
with open(
    os.path.join(os.path.dirname(__file__), "templates", "blendxcoursecreator", "tasks", "mysql", "init"),
    encoding="utf-8",
) as fi:
    mysql_init_task = fi.read()
hooks.Filters.CLI_DO_INIT_TASKS.add_item(("mysql", mysql_init_task))

# BlendxCCApp init task
with open(
    os.path.join(os.path.dirname(__file__), "templates", "blendxcoursecreator", "tasks", "blendxccapp", "init"),
    encoding="utf-8",
) as fi:
    blendxccapp_init_task = fi.read()
hooks.Filters.CLI_DO_INIT_TASKS.add_item(("blendxccapp", blendxccapp_init_task))


########################################
# MOUNT MANAGEMENT
########################################

@hooks.Filters.COMPOSE_MOUNTS.add()
def _mount_blendxccapp(volumes: list[tuple[str, str]], name: str) -> list[tuple[str, str]]:
    """
    When mounting blendxccapp with `--mount=/path/to/blendxccapp`,
    bind-mount the host repo in the blendxccapp container.
    """
    if name == "blendxccapp":
        path = "/app"
        volumes += [
            ("blendxccapp", path),
            ("blendxccapp-celery", path),
        ]
    return volumes

# Bind-mount repo at build-time, both for prod and dev images
@hooks.Filters.IMAGES_BUILD_MOUNTS.add()
def _mount_blendxccapp_on_build(mounts: list[tuple[str, str]], host_path: str) -> list[tuple[str, str]]:
    path_basename = os.path.basename(host_path)
    if path_basename == "blendxccapp":
        mounts.append(('blendxccapp', "blendxccapp-src"))
        mounts.append(("blendxccapp-dev", "blendxccapp-src"))
    return mounts


########################################
# PUBLIC HOSTS
########################################

@hooks.Filters.APP_PUBLIC_HOSTS.add()
def _blendxccapp_public_hosts(hosts: list[str], context_name: str) -> list[str]:
    if context_name == "dev":
        hosts += ["{{ BLENDXCCAPP_HOST }}:8000"]
    else:
        hosts += ["{{ BLENDXCCAPP_HOST }}"]
    return hosts


#######################################
# CUSTOM MFE APPS
#######################################

def _get_mfe_version():
    load_dotenv()
    return os.getenv("COURSE_CREATOR_MFE_VERSION", "master")

def _get_github_pat():
    load_dotenv()
    if os.getenv("GITHUB_PAT"):
        return f"{os.getenv('GITHUB_PAT')}@"
    else:
        return ""


@MFE_APPS.add()
def _add_my_mfe(mfes):

    mfes["course-creator"] = {
        "repository": f"https://{_get_github_pat()}github.com/blend-ed/frontend-app-course-creator.git",
        "port": 8009,
        "version": _get_mfe_version()
    }

    return mfes


#######################################
# CUSTOM CLI COMMANDS
#######################################

# BlendxCCApp custom commands
@click.command()
def blendxccapp_shell() -> list[tuple[str, str]]:
    """Open Python shell in blendxccapp container"""
    return [("blendxccapp", "python")]

hooks.Filters.CLI_DO_COMMANDS.add_item(blendxccapp_shell)