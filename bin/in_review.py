#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""This script shows rough information from Bugzilla and GitHub for a given period
of time denoted by year and (optionally) quarter.

This script was never designed. Rather, it started as a single-celled organism
subjected to heavy doses of gamma radiation. Over time, quarter after quarter,
it grew into the monstrosity of procedural generation you see before you.

This script is poorly maintained. Other than bombarding it with radiation every
quarter and occasionally trimming off the really gross looking bits, it evolves
of its own accord.


API tokens
==========

Running this script requires a Bugzilla API token and a GitHub token.

Bugzilla API token is given via the ``BUGZILLA_API_KEY`` environment variable
or stored in plain text in ``~/.bugzilla`` file.

GitHub API token is given via the ``GITHUB_API_KEY`` environment variable or
stored in plain text in ``~/.githubauth`` file. In both cases, the "token" is
composed of the GitHub username, a colon, then the API key. the form is::

    USERNAME:APIKEY

For example::

    janetexample:abcdef0000000000000000000000000000000000


Usage
=====

To use this:

1. Create a virtual environment with Python 3::

       mkvirtualenv --python=/usr/bin/python3 inreview

2. Install the dependencies::

       pip install bugzilla github3.py requests

3. Either set the environment variables or create the files required for
   tokens.

4. Run from the repository root::

       BUGZILLA_API_KEY=xyz python bin/in_review.py <YEAR> [<QUARTER>]

"""

import datetime
import os
import sys
import textwrap


try:
    import bugzilla
    import github3
except ImportError as ie:
    print(ie)
    print('Please run "pip install requests bugzilla github3.py".')
    sys.exit(1)


BUGZILLA_API_URL = 'https://bugzilla.mozilla.org/rest/'
BUGZILLA_PRODUCTS = [
    # product, list of components (use - to remove a component)
    ('Socorro', ['-Tecken Integration'])
]

GITHUB_REPOS = [
    # Main Socorro repository
    ('mozilla-services', 'socorro'),

    # New Socorro collector
    ('mozilla-services', 'antenna'),

    # Pigeon
    ('mozilla-services', 'socorro-pigeon'),

    # Symbols server
    # ('mozilla-services', 'tecken'),

    # New Socorro processor
    # ('mozilla-services', 'jansky'),
]

QUARTERS = {
    1: [(1, 1), (3, 31)],
    2: [(4, 1), (6, 30)],
    3: [(7, 1), (9, 30)],
    4: [(10, 1), (12, 31)]
}

USAGE = 'Usage: in_review.py <YEAR> [<QUARTER>]'
HEADER = 'in_review.py: find out what happened year or quarter!'


all_people = set()


def str_to_dt(text):
    return datetime.datetime.strptime(text + '+0000', '%Y-%m-%dT%H:%M:%SZ%z')


def dt_to_str(dt):
    """Converts a dt value to a YYYY-MM-DD string

    If the dt value is a string, it gets returned. If it's a datetime.datetime
    or a datetime.date, then it gets formatted as YYYY-MM-DD and returned.

    :arg varies dt: the date to convert

    :returns: date as a YYYY-MM-DD string

    """
    if isinstance(dt, (datetime.datetime, datetime.date)):
        return dt.strftime('%Y-%m-%d')
    return dt


def wrap(text, indent='    ', subsequent='    '):
    text = text.split('\n\n')
    text = [textwrap.fill(part, expand_tabs=True, initial_indent=indent,
                          subsequent_indent=subsequent)
            for part in text]
    return '\n\n'.join(text)


def truncate(text, length):
    if len(text) > length:
        return text[:length - 3] + '...'
    return text


class BugzillaBrief(bugzilla.Bugzilla):
    def get_history(self, bugid):
        """Retrieves the history for a bug"""
        return self._get('bug/{bugid}/history'.format(bugid=bugid))

    def get_bugs_created(self, products, from_date, to_date):
        """Retrieves summary of all bugs created between two dates for a given product

        :arg list products: products and components to look at
        :arg from_date: greater than or equal to this date
        :arg to_date: less than or equal to this date

        :returns: dict with "count", "creator_count", and "bugs" keys

        """
        ret = {
            'count': 0,
            'creators': {},
            'bugs': []
        }

        for product, comps in products:
            exclude_comp = [c[1:] for c in comps if c.startswith('-')]
            include_comp = [c for c in comps if not c.startswith('-')]

            terms = [
                {'product': product},
                {'f1': 'creation_ts'},
                {'o1': 'greaterthaneq'},
                {'v1': dt_to_str(from_date)},
                {'f2': 'creation_ts'},
                {'o2': 'lessthaneq'},
                {'v2': dt_to_str(to_date)},
            ]
            resp = self.search_bugs(terms=terms)

            creation_count = len(resp.bugs)
            creators = {}
            for bug in resp.bugs:
                if exclude_comp and bug['component'] in exclude_comp:
                    continue
                if include_comp and bug['component'] not in include_comp:
                    continue

                # FIXME(willkg): Move name figuring this to another function
                creator = bug.get('creator_detail', {}).get('real_name', None)
                if not creator:
                    creator = bug.get('creator', '').split('@')[0]
                creators[creator] = creators.get(creator, 0) + 1

            ret['count'] = ret['count'] + creation_count
            for key, val in creators.items():
                ret['creators'][key] = ret['creators'].get(key, 0) + val
            ret['bugs'].extend(resp.bugs)

        return ret

    def get_resolution_history_item(self, bug):
        history = self.get_history(bug['id'])
        for item in reversed(history.bugs[0]['history']):
            # See if this item in the history is the resolving event. If it is,
            # then we know who resolved the bug and we can stop looking at
            # history.
            changes = [
                change for change in item['changes']
                if change['field_name'] == 'status' and change['added'] == 'RESOLVED'
            ]

            if changes:
                bug['ir_resolution_item'] = item
                return

        # None of the history was a resolution, so we mark it as None.
        bug['ir_resolution_item'] = None

    def get_bugs_resolved(self, products, from_date, to_date):
        ret = {
            'count': 0,
            'resolvers': {},
            'resolved_map': {},
            'bugs': []
        }

        for product, comps in products:
            exclude_comp = [c for c in comps if c.startswith('-')]
            include_comp = [c for c in comps if not c.startswith('-')]

            terms = [
                {'product': product},
                {'f1': 'cf_last_resolved'},
                {'o1': 'greaterthaneq'},
                {'v1': dt_to_str(from_date)},
                {'f2': 'cf_last_resolved'},
                {'o2': 'lessthan'},
                {'v2': dt_to_str(to_date)},
            ]
            resp = self.search_bugs(terms=terms)

            resolved_count = len(resp.bugs)
            resolved_map = {}
            resolvers = {}

            for bug in resp.bugs:
                if exclude_comp and bug['component'] in exclude_comp:
                    continue
                if include_comp and bug['component'] not in include_comp:
                    continue
                resolution = bug['resolution']
                resolved_map[resolution] = resolved_map.get(resolution, 0) + 1

                assigned_to = bug.get('assigned_to_detail', {}).get('real_name', None)
                if not assigned_to:
                    assigned_to = bug.get('assigned_to', 'unknown').split('@')[0]

                self.get_resolution_history_item(bug)
                if 'nobody' in assigned_to.lower():
                    # If no one was assigned, we give "credit" to whoever triaged
                    # the bug. We go through the history in reverse order because
                    # the "resolver" is the last person to resolve the bug.
                    assigned_to = bug['ir_resolution_item']['who']

                if assigned_to:
                    if '@' in assigned_to:
                        assigned_to = assigned_to.split('@')[0]

                resolvers[assigned_to] = resolvers.get(assigned_to, 0) + 1

            ret['count'] += resolved_count
            for key, val in resolvers.items():
                ret['resolvers'][key] = ret['resolvers'].get(key, 0) + val
            for key, val in resolved_map.items():
                ret['resolved_map'][key] = ret['resolved_map'].get(key, 0) + val
            ret['bugs'].extend(resp.bugs)

        return ret


class GitHubBrief:
    def __init__(self, username=None, password=None):
        if username and password:
            self.client = github3.login(
                username=username,
                password=password,
                two_factor_callback=self.two_factor_callback
            )
        else:
            self.client = github3.GitHub()

    def two_factor_callback():
        code = ''
        while not code:
            code = input('Enter 2fa: ').strip()
        return code

    def merged_pull_requests(self, owner, repo, from_date, to_date):
        from_date = dt_to_str(from_date)
        to_date = dt_to_str(to_date)

        merged_prs = []

        repo = self.client.repository(owner=owner, repository=repo)
        resp = repo.iter_pulls(state='closed', sort='updated', direction='desc')

        # We're sorting by "updated", but that could be a comment and not
        # necessarily a merge event, so we fudge this by continuing N past the
        # from_date
        N = 20
        past_from_date = 0

        for pr in resp:
            if not pr.merged_at:
                continue

            if dt_to_str(pr.merged_at) > to_date:
                # Outside the range, so continue
                continue

            if dt_to_str(pr.merged_at) < from_date:
                # Outside the range, but since PRs are ordered by updated descending, we
                # continue another N past the from_date and then break
                if past_from_date > N:
                    break
                past_from_date += 1
                continue

            merged_prs.append(pr)

        return {
            'prs': merged_prs
        }


def statistics(ages_items):
    ages = [item[0] for item in ages_items]
    return {
        'min': min(ages_items, key=lambda item: item[0]),
        'max': max(ages_items, key=lambda item: item[0]),
        'average': sum(ages) / len(ages),
        'median': sorted(ages)[int(len(ages) / 2)]
    }


def get_bugzilla_token():
    """Retrieves Bugzilla API token from env or ~/.bugzilla file"""
    api_key = os.environ.get('BUGZILLA_API_KEY')
    if api_key:
        return api_key

    path = os.path.expanduser('~/.bugzilla')
    if os.path.exists(path):
        return open(path, 'r').read().strip()

    return None


def print_bugzilla_stats(from_date, to_date):
    api_key = get_bugzilla_token()
    if not api_key:
        print(
            'You need to specify a Bugzilla API key either in the BUGZILLA_API_KEY '
            'environment variable or in the ~/.bugzilla file.'
        )
        return

    bugzilla_brief = BugzillaBrief(
        url=BUGZILLA_API_URL,
        api_key=api_key
    )

    # Bug creation stats

    created_stats = bugzilla_brief.get_bugs_created(BUGZILLA_PRODUCTS, from_date, to_date)

    print('  Bugs created: %s' % created_stats['count'])
    print('  Creators: %s' % len(created_stats['creators']))
    print('')

    creators = sorted(created_stats['creators'].items(), reverse=True, key=lambda item: item[1])
    for person, count in creators:
        print('   %34s : %s' % (person[:30], count))
        all_people.add(person)
    print('')

    # Bug resolution stats

    resolved_stats = bugzilla_brief.get_bugs_resolved(BUGZILLA_PRODUCTS, from_date, to_date)

    print('  Bugs resolved: %s' % resolved_stats['count'])
    print('')
    for resolution, count in resolved_stats['resolved_map'].items():
        print('   %34s : %s' % (resolution, count))

    print('')
    print('  Resolvers: %s' % len(resolved_stats['resolvers']))
    print('')
    resolvers = sorted(resolved_stats['resolvers'].items(), reverse=True,
                       key=lambda item: item[1])
    for person, count in resolvers:
        print('   %34s : %s' % (person[:30], count))
        all_people.add(person)

    # Commenter stats

    person_to_comment_count = {}
    for bug in resolved_stats['bugs']:
        comments = bugzilla_brief.get_comments(bug['id'])
        # The Bugzilla REST api has some interesting things about it.
        for comment in comments['bugs'][str(bug['id'])]['comments']:
            commenter = comment['author']
            if '@' in commenter:
                commenter = commenter.split('@')[0]

                person_to_comment_count[commenter] = person_to_comment_count.get(commenter, 0) + 1
            all_people.add(commenter)

    print('')
    print('  Commenters: %s' % len(person_to_comment_count))
    print('')
    commenters = sorted(person_to_comment_count.items(), reverse=True, key=lambda item: item[1])
    for person, count in commenters:
        print('   %34s : %s' % (person[:30], count))

    tracker_bugs = []
    for bug in resolved_stats['bugs']:
        if '[tracker]' in bug['summary']:
            tracker_bugs.append(bug)

    # Tracker bugs

    print('')
    print('  Tracker bugs: %s' % len(tracker_bugs))
    print('')
    for bug in tracker_bugs:
        print(wrap('  %s: %s' % (bug['id'], bug['summary']), subsequent='        '))

    # Statistics

    stats = statistics([
        (
            (str_to_dt(bug['ir_resolution_item']['when']) - str_to_dt(bug['creation_time'])).days,
            bug
        )
        for bug in resolved_stats['bugs']
    ])

    print('')
    print('  Statistics')
    print('')
    print('      Youngest bug : %-2.1fd: %s: %s' % (
        stats['min'][0],
        stats['min'][1]['id'],
        truncate(stats['min'][1]['summary'], 50)
    ))
    print('   Average bug age : %-2.1fd' % stats['average'])
    print('    Median bug age : %-2.1fd' % stats['median'])
    print('        Oldest bug : %-2.1fd: %s: %s' % (
        stats['max'][0],
        stats['max'][1]['id'],
        truncate(stats['max'][1]['summary'], 50)
    ))


def get_github_auth():
    """Retrieves github auth credentials from a ~/.githubauth file"""
    user_token = os.environ.get('GITHUB_API_KEY')
    if user_token:
        return user_token.split(':')

    path = os.path.expanduser('~/.githubauth')
    if os.path.exists(path):
        return open(path, 'r').read().strip().split(':')

    return None


def print_github_stats(from_date, to_date):
    auth = get_github_auth()
    if auth:
        github_brief = GitHubBrief(auth[0], auth[1])
    else:
        github_brief = GitHubBrief()

    merged_prs = {}
    for owner, repo in GITHUB_REPOS:
        merged_prs[(owner, repo)] = github_brief.merged_pull_requests(
            owner, repo, from_date, to_date
        )

    for key, prs in sorted(merged_prs.items()):
        # Person -> pull requests
        committers = {}

        # Person -> (# inserted, # deleted)
        changes = {}

        # These are total line counts
        total_added = total_deleted = 0

        # This is the dict of all files that changed to number of times they
        # changed
        files_changed = {}

        prs = prs['prs']
        print('  %s: %s prs' % ('%s/%s' % key, len(prs)))
        print('')
        if prs:
            for pr in prs:
                user_name = str(pr.user)
                committers.setdefault(user_name, []).append(pr)

                for pr_file in pr.iter_files():
                    added, deleted, changed = changes.get(user_name, (0, 0, {}))
                    changed[pr_file.filename] = changed.get(pr_file.filename, 0) + 1

                    changes[user_name] = (
                        added + pr_file.additions,
                        deleted + pr_file.deletions,
                        changed
                    )

                    total_added += pr_file.additions
                    total_deleted += pr_file.deletions
                    files_changed[pr_file.filename] = files_changed.get(pr_file.filename, 0) + 1

            # Figure out prs, additions, and deletions per person
            print('    Committers:')
            committers = sorted(committers.items(), key=lambda item: len(item[1]), reverse=True)
            for user_name, committed_prs in committers:
                print(' %20s : %5s  (%6s, %6s, %4s files)' % (
                    user_name,
                    len(committed_prs),
                    '+' + str(changes[user_name][0]),
                    '-' + str(changes[user_name][1]),
                    str(len(changes[user_name][2]))
                ))
                all_people.add(user_name)

            print('')
            print('                Total :        (%6s, %6s, %4s files)' % (
                '+' + str(total_added),
                '-' + str(total_deleted),
                str(len(files_changed))
            ))

            print('')
            print('    Most changed files:')
            most_changed_files = sorted(files_changed.items(), key=lambda item: item[1], reverse=True)
            for fn, count in most_changed_files[:10]:
                print('      %s (%d)' % (fn, count))

            print('')
            print('    Age stats:')
            stats = statistics([
                ((pr.merged_at - pr.created_at).days, pr)
                for pr in prs
            ])
            print('          Youngest PR : %-2.1fd: %s: %s' % (
                stats['min'][0],
                stats['min'][1].number,
                truncate(stats['min'][1].title, 50)
            ))
            print('       Average PR age : %-2.1fd' % stats['average'])
            print('        Median PR age : %-2.1fd' % stats['median'])
            print('            Oldest PR : %-2.1fd: %s: %s' % (
                stats['max'][0],
                stats['max'][1].number,
                truncate(stats['max'][1].title, 50)
            ))

        print('')

    print('')
    print('  All repositories:')
    print('')
    print('    Total merged PRs: %s' % sum(len(prs['prs']) for prs in merged_prs.values()))
    print('')


def print_all_people():
    # We do this sorting thing to make it a little easier to suss out
    # duplicates since we're pulling names from three different forms between
    # Bugzilla and git.

    # You're still going to have to go through it by hand to remove duplicates.
    people = sorted(all_people, key=lambda a: a.lower())

    for person in people:
        print('  ' + person)


def print_header(text, level=1):
    level_to_char = {
        1: '=',
        2: '-',
    }
    print('')
    print(text)
    print(level_to_char[level] * len(text))
    print('')


def main(argv):
    if len(argv) < 1:
        print(USAGE)
        print('Error: Must specify year or year and quarter. Examples:')
        print('in_review.py 2014')
        print('in_review.py 2014 1')
        return 1

    print(HEADER)

    year = int(argv[0])
    if len(argv) == 1:
        from_date = datetime.date(year, 1, 1)
        to_date = datetime.date(year, 12, 31)

        print_header('Year %s (%s -> %s)' % (year, from_date, to_date))

    else:
        quarter = int(argv[1])
        quarter_dates = QUARTERS[quarter]

        from_date = datetime.date(year, quarter_dates[0][0], quarter_dates[0][1])
        to_date = datetime.date(year, quarter_dates[1][0], quarter_dates[1][1])

        print_header('Quarter %sq%s (%s -> %s)' % (year, quarter, from_date, to_date))

    print_header('Bugzilla')
    print_bugzilla_stats(from_date, to_date)

    print_header('GitHub')
    print_github_stats(from_date, to_date)

    print_header('Contributors')
    print_all_people()


if __name__ == '__main__':
    if not sys.version.startswith('3'):
        print('Requires Python 3.')
        sys.exit(1)

    sys.exit(main(sys.argv[1:]))
