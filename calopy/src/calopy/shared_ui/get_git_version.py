import subprocess
import gitlab
import os


def get_git_commit():
    try:
        commit_id = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
        return commit_id
    except Exception as e:
        print(f"Error detecting git version: {e}")
        return "unknown_version"

def get_git_version_tag():
    version_file_path = "../VERSION"
    if os.path.isfile(version_file_path):
        try:
            with open(version_file_path, "r") as f:
                version = f.read().strip()
                if version:
                    return version
        except Exception as e:
            print(f"Error reading VERSION file: {e}")
    try:
        #tag_id = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).strip().decode("utf-8")

        git_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode("utf-8")
        return "Branch: " + git_branch + "; commit: " + get_git_commit()
    except Exception as e:
        print(f"Error detecting git version: {e}")
        return "unknown_version"

def get_calopy_gitlab_version():
    try:
        gl = gitlab.Gitlab()
        project = gl.projects.get(44609436, lazy=True)
        releases = project.releases.list(get_all=False)
        return releases[0].tag_name

    except Exception as e:
        print(f"Error detecting git version: {e}")
        return "unknown_version"