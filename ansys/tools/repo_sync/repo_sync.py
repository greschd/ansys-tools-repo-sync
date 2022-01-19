import os
import shutil
import stat
import subprocess
import time

import github

# import git  # To be investigated.


def synchronize(
    token: str = None,
     authoritative_repo: str = r"https://github.com/pyansys/synchronization-demo",
     repository: str = "synchronization-demo2",
     organization: str = "pyansys",
     filename: str = None
):
    """Synchronize the content of two different repositories.
    - clone the content of the reference repository
    - create a new branch
    - add/ remove some folders/files.
    - push the modification into the destination repository
    - create a pull request to merge the modification into the main branch of the destination repository
    """

    # use secret
    if not token:
        token = os.environ.get("GH_PAT")

    user_name = os.environ.get("git_bot_user")
    organization = "pyansys"
    branch_name = "sync/sync_branch"

    # Clone the repo.
    process = subprocess.Popen(
        #["git", "clone", f"{authoritative_repo}", "--depth", "1"],
        # see https://stackoverflow.com/questions/28983842/remote-rejected-shallow-update-not-allowed-after-changing-git-remote-url
        ["git", "clone", f"{authoritative_repo}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    # Change the remote url
    time.sleep(5)
    process = subprocess.Popen(
        ["git", "remote", "set-url", "origin", f"https://{token}@github.com/{organization}/{repository}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["git", "remote", "set-url", "origin", f"https://{token}@github.com/{organization}/{repository}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    # # Set the username
    # process = subprocess.Popen(
    #     'git config user.name "Max"',
    #     shell=True,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    # stdout, stderr = process.communicate()

    # os.chdir(repository)
    os.chdir(authoritative_repo.split("/")[-1])

    # Create a new branch.
    try:
        process = subprocess.Popen(
            ["git", "checkout", "-b", branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
    except:
        process = subprocess.Popen(
            ["git", "checkout", branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

    # Add a sample file.
    with open("testing.txt", "w") as f:
        f.write("hello world")

    # unsafe, should add specific file or directory
    if not filename:
        process = subprocess.Popen(
            ["git", "add", "--a"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
    else:
        process = subprocess.Popen(
            ["git", "add", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

    if filename:
        message = f"Add {filename}"
    else:
        message = f"Copy all files located into the {repository} repository from branch {branch_name}."

        process = subprocess.Popen(
            ["git", "commit", "-am", message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

    # no history in common with main
        process = subprocess.Popen(
            ["git", "pull", "origin", "main", "--allow-unrelated-histories", "-X", "theirs"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        process = subprocess.Popen(
            ["git", "commit", "-am", "merge"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

    process = subprocess.Popen(
        ["git", "push", "-u", "origin", branch_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    # Create pull request.
    gh = github.Github(token)
    repo = gh.get_repo(f"{organization}/{repository}")
    pr = repo.create_pull(title=message, body=message, head=branch_name, base="main")

    # Delete the git repository that was created.
    parent_folder = os.path.dirname(os.getcwd())
    os.chdir(parent_folder)
    folder_name = authoritative_repo.split("/")[-1]
    shutil.rmtree(os.path.join(parent_folder, folder_name), onerror=on_rm_error)


def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


if __name__ == "__main__":
    synchronize()
