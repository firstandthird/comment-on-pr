import json
import os

from github import Github


def read_json(filepath):
    """
    Read a json file as a dictionary.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict

    """
    with open(filepath, 'r') as f:
        return json.load(f)


def get_actions_input(input_name):
    """
    Get a Github actions input by name.

    Parameters
    ----------
    input_name : str

    Returns
    -------
    action_input : str

    Notes
    -----
    GitHub Actions creates an environment variable for the input with the name:

    INPUT_<CAPITALIZED_VARIABLE_NAME> (e.g. "INPUT_FOO" for "foo")

    References
    ----------
    .. [1] https://help.github.com/en/actions/automating-your-workflow-with-github-actions/metadata-syntax-for-github-actions#example  # noqa: E501

    """
    return os.getenv('INPUT_{}'.format(input_name).upper())


def load_template(filename):
    """
    Load a template.

    Parameters
    ----------
    filename : template file name

    Returns
    -------
    template : str

    """
    template_path = os.path.join('.github/workflows', filename)
    with open(template_path, 'r') as f:
        return f.read()

def extract_branch_name(ref):
    # Split the string by '/'
    parts = ref.split('/')
    # Return the last part (branch name)
    return parts[-1] if parts else None

def main():
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))    
    branch_name = extract_branch_name(event['ref'])
    branch_author = event["repository"]["full_name"].split('/')[0]
    branch_label = branch_author + ":" + branch_name
    print(branch_label)
    repo = gh.get_repo(event['repository']['full_name'])
    prs = repo.get_pulls(state='open', sort='created', head=branch_label)
    pr = prs[0]

    # the host repo should have a 'uat.md' defined in the workflows directory
    template = load_template('uat.md')
    # build a comment
    pr_info = {
        'pull_id': pr.number,
        'branch_name': branch_name
    }
    new_comment = template.format(**pr_info)
    print(new_comment)
    # check if this pull request has a duplicated comment
    old_comments = [c.body for c in pr.get_issue_comments()]
    if new_comment in old_comments:
        print('This pull request already a duplicated comment.')
        exit(0)

    # add the comment
    pr.create_issue_comment(new_comment)


if __name__ == '__main__':
    main()
