#!/usr/bin/env python
import numpy as np
import seaborn as sns
sns.set(color_codes=True)
import matplotlib.mlab as mlab
import matplotlib as mpl
import matplotlib.pyplot as plt
curtail_idx = [3, 0, 1, 0, 3, 1]
curtail_begidx = [0, 0, 2, 0, 0, 0]
for idx, fn in enumerate([
        'EmploymentMembership_events_organization_count_histogram.header.count.member.tsv',
        'InvestorShareholder_events_organization_count_histogram.header.count.member.tsv',
        'MemberOriginReligionEthnicity_events_affiliatedEntity_count_histogram.header.count.member.tsv',
        'Membership_events_organization_count_histogram.header.count.member.tsv',
        'Resident_events_location_count_histogram.header.count.member.tsv',
        'StudentAlum_events_organization_count_histogram.header.count.member.tsv']):
    print idx
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    data = np.array([[int(_) for _ in e.strip().split()] for e in open(fn)])
    area = 1  # np.sum(data[:, 1] * data[:, 0])
    points_shown = range(curtail_begidx[idx], data.shape[0] - curtail_idx[idx])
    points_not_shown = (range(curtail_begidx[idx])
                        + range(data.shape[0] - curtail_idx[idx], data.shape[0]))
    x_data = data[points_shown, 1]
    y_data = data[points_shown, 0]
    x_not_shown = data[points_not_shown, 1]
    x_fake = [min(100, e) for e in x_not_shown]
    y_fake = [max(y_data) + 100] * len(points_not_shown)
    artists = plt.bar(list(x_data) + list(x_fake), list(y_data) + y_fake)
    for a_idx, (a, pt, x, y, xns) in enumerate(zip(
            artists[-len(points_not_shown):],
            points_not_shown,
            x_fake,
            y_fake, x_not_shown)):
        a.set_facecolor('r')
        text = str(data[pt, 0])
        if x != xns:
            text = 'x=%d, ' % xns + text
        ax1.add_artist(mpl.text.Text(
            x=x, y=y - 100 + 10 * a_idx, horizontalalignment='left',
            verticalalignment='left', text=text,
            rotation=45, family='monospace', weight='bold'))
    plt.ylabel('Number of organization')
    plt.xlabel('Number of members')
    plt.title(fn.split('_events_')[0])
    plt.show()
